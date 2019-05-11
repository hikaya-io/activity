# -*- coding: utf-8 -*-
import copy
import types
import sys

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum, Avg, Count, Max, Min, F
from django.http import HttpResponseRedirect
from django.utils import formats

map_aggregates = ((Sum, "__sum"), (Count, "__count"), (Avg, "__avg"),
                  (Max, "__max"), (Min, "__min"), (F, "__expression"))


def function_builder(name_function, attr, title_column):
    def new_function(self, obj):
        return getattr(obj, attr)
    new_function.__name__ = name_function
    if title_column:
        new_function.short_description = title_column
    new_function.admin_order_field = attr
    new_function.allow_tags = True
    return new_function


class ChangeListChartReport(ChangeList):

    result_aggregate = []

    def get_queryset(self, request):

        qs = super(ChangeListChartReport, self).get_queryset(request)

        if self.model_admin.annotate_fields:
            # qs = self.root_queryset

            # estudar essa parte, esta estranho
            if self.model_admin.group_by:
                qs = qs.values(*self.model_admin.group_by)

            # faz uma copia antes de chamar o metodo annotate, pois para campos aggregate que não
            # representam um campo annotate, não se pode ter o annotate na query
            self.query_to_normal_aggregate = qs

            # print "self.model_admin.annotate_fields"
            # print self.model_admin.annotate_fields

            # qs = qs.annotate(*self.model_admin.annotate_fields_2, **self.model_admin.annotate_fields)
            qs = qs.annotate(**self.model_admin.annotate_fields)

            # Set ordering.
            ordering = self.get_ordering(request, qs)
            if self.model_admin.group_by:

                if '-pk' in ordering:
                    ordering.remove('-pk')
                if 'pk' in ordering:
                    ordering.remove('pk')
            qs = qs.order_by(*ordering)

            # Apply search results
            qs, search_use_distinct = self.model_admin.get_search_results(
                request, qs, self.query)

            # print qs.query
            # print "get_queryset"
        else:
            self.query_to_normal_aggregate = qs

        # print "#### query final ####"
        # print qs.query

        return qs

    def get_results(self, request):
        super(self.__class__, self).get_results(request)

        if self.result_list and isinstance(self.result_list[0], dict):
            pk_name = self.model._meta.pk.name
            try:
                ids = [i[pk_name] for i in self.result_list]
            except KeyError:
                ids = []

            result_list_in_model = self.model.objects.filter(pk__in=ids)
            result_list_in_model_dict = {}
            for item_model in result_list_in_model:
                result_list_in_model_dict[getattr(
                    item_model, pk_name)] = item_model

            new_result_list = []
            for row in self.result_list:
                if pk_name in row and result_list_in_model_dict:
                    new_row = copy.deepcopy(
                        result_list_in_model_dict[row[pk_name]])
                else:
                    new_row = self.model()

                for key, value in list(row.items()):

                    setattr(new_row, key, value)

                new_result_list.append(new_row)

            self.result_list = new_result_list

        self.get_result_aggregate()

    def get_result_aggregate(self):
        # print self.list_display

        result_aggregate = []
        result_aggregate_by_column = []
        result_aggregate_queryset = None
        result_aggregate_from_normal_queryset = {}
        result_aggregate_from_annotate_queryset = {}

        qs = self.queryset
        if self.model_admin.aggregate_fields_from_normal:
            result_aggregate_from_normal_queryset = self.query_to_normal_aggregate.aggregate(
                *self.model_admin.aggregate_fields_from_normal)

        if self.model_admin.aggregate_fields_from_annotate:
            result_aggregate_from_annotate_queryset = qs.aggregate(
                *self.model_admin.aggregate_fields_from_annotate)

        result_aggregate_queryset = dict(
            result_aggregate_from_normal_queryset, **result_aggregate_from_annotate_queryset)

        def get_result_aggregate(aggregate):
            pos_value_place_holder = aggregate[2].find("%value")

            aggregate_string_replace = "{0} {1}"
            if pos_value_place_holder != -1:
                aggregate_string_replace = aggregate[2].replace(
                    "%value", "{1}")

            if isinstance(result_aggregate_queryset[aggregate[0]], float):
                label_foot = formats.number_format(
                    result_aggregate_queryset[aggregate[0]], 2)
            else:
                label_foot = formats.localize(
                    result_aggregate_queryset[aggregate[0]], use_l10n=True)

            label_foot = aggregate_string_replace.format(
                aggregate[2], label_foot)
            return label_foot

        if result_aggregate_queryset:
            for column in self.list_display:
                result_aggregate_temp = []
                if column in self.model_admin.map_list_display_and_aggregate:
                    for aggregate in self.model_admin.map_list_display_and_aggregate[column]:
                        result_aggregate_temp.append(
                            get_result_aggregate(aggregate))

                if result_aggregate_temp:
                    result_aggregate_by_column.append(
                        "<br>".join(result_aggregate_temp))
                else:
                    result_aggregate_by_column.append("")

            for aggregate in self.model_admin.map_summary_aggregate:
                result_aggregate.append(get_result_aggregate(aggregate))

        self.result_aggregate = result_aggregate
        self.result_aggregate_by_column = result_aggregate_by_column


class AdminExceptionFieldsFilterMixin(admin.ModelAdmin):

    exception_fields_filter = ()

    def lookup_allowed(self, lookup, value):

        return True


class ChartReportAdmin(admin.ModelAdmin):

    report_annotates = ()
    report_aggregates = ()
    group_by = ()
    list_display_links = None

    class Media:
        css = {
            'all': ('admin/css/django_admin_report/django_admin_report.css',)
        }

    def __init__(self, model, admin_site):

        self.annotate_fields = {}
        self.aggregate_fields_from_normal = []
        self.aggregate_fields_from_annotate = []
        self.map_list_display_and_aggregate = {}
        self.map_summary_aggregate = []

        for annotate in self.report_annotates:
            for func, end_field_name in map_aggregates:
                if func == annotate[1]:
                    name_field_annotate = "{}{}".format(
                        annotate[0], end_field_name)
                    self.annotate_fields.update(
                        {name_field_annotate: annotate[1](annotate[0])})
                    self.addMethod(function_builder(
                        name_field_annotate, name_field_annotate, annotate[2] if len(annotate) == 3 else None))
                    break

        for aggregate in self.report_aggregates:
            for func, end_field_name in map_aggregates:
                if func == aggregate[1]:
                    copy_aggregate = list(aggregate[:])
                    name_field_aggregate = "{0}{1}".format(
                        aggregate[0], end_field_name)

                    copy_aggregate[0] = name_field_aggregate

                    new_label = "{0}{1}".format(aggregate[0], end_field_name)
                    if len(copy_aggregate) == 2:
                        copy_aggregate.append(new_label)
                    elif not copy_aggregate[2]:
                        copy_aggregate[2] = new_label

                    # significa que foi especificado em qual coluna deve aparecer o valor agregado
                    if len(copy_aggregate) == 4:
                        column_display_list = aggregate[3]
                    else:
                        column_display_list = aggregate[0]
                        if column_display_list not in self.list_display:
                            column_display_list = new_label

                    if column_display_list not in self.map_list_display_and_aggregate:
                        self.map_list_display_and_aggregate[column_display_list] = [
                        ]

                    self.map_list_display_and_aggregate[column_display_list].append(
                        copy_aggregate)
                    self.map_summary_aggregate.append(copy_aggregate)
                    break

            if aggregate[0] in self.annotate_fields:
                self.aggregate_fields_from_annotate.append(
                    aggregate[1](aggregate[0]))
            else:
                self.aggregate_fields_from_normal.append(
                    aggregate[1](aggregate[0]))

        self.list_max_show_all = sys.maxsize

        super(ChartReportAdmin, self).__init__(model, admin_site)

    def add_view(self, request, form_url='', extra_context=None):
        # volta sempre para a mesma pagina
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    def addMethod(self, func):
        return setattr(self, func.__name__, types.MethodType(func, self))

    def get_changelist(self, request, **kwargs):
        return ChangeListChartReport
