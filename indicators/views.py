#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict

from urllib.parse import urlparse
import re
import json

from rest_framework.permissions import IsAuthenticated

from activity.permissions import IsReadOnly
from .export import IndicatorResource, CollectedDataResource
from .serializers import (PeriodicTargetSerializer, CollectedDataSerializer, IndicatorSerializer,
                          IndicatorTypeSerializer, DataCollectionFrequencySerializer, LevelSerializer,
                          ObjectiveSerializer,
                          DisaggregationTypeSerializer, DisaggregationLabelSerializer, DisaggregationValueSerializer,
                          DocumentationSerializer)

from .tables import IndicatorDataTable
from .forms import (
    IndicatorForm, CollectedDataForm, StrategicObjectiveForm, ObjectiveForm, LevelForm
)
from .models import (
    Indicator, PeriodicTarget, DisaggregationLabel, DisaggregationValue,
    DisaggregationType, CollectedData, IndicatorType, Level, ExternalServiceRecord,
    ExternalService, ActivityTable, StrategicObjective, Objective, DataCollectionFrequency, ActivityUser
)

from django.db.models import Count, Sum, Min, Q
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import View
from django.views.generic import View as GView
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import PermissionDenied
from django.core import serializers
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django_tables2 import RequestConfig

from workflow.models import (
    Program, SiteProfile, Country, Sector, ActivitySites, FormGuidance,
    Documentation, Organization
)
from workflow.mixins import AjaxableResponseMixin
from workflow.admin import CountryResource
from workflow.forms import FilterForm
from feed.serializers import FlatJsonSerializer
from activity.util import get_country, get_table

import requests
from weasyprint import HTML, CSS
from datetime import datetime
from dateutil.relativedelta import relativedelta
from rest_framework import generics, status
from rest_framework.response import Response


def generate_periodic_target_single(tf, start_date, nth_target_period,
                                    target_frequency_custom=''):
    i = nth_target_period
    j = i + 1
    target_period = ''

    if tf == Indicator.LOP:
        lop_target = Indicator.TARGET_FREQUENCIES[Indicator.LOP-1][1]
        return {'period': lop_target}
    elif tf == Indicator.MID_END:
        return [{'period': 'Midline'}, {'period': 'Endline'}]
    elif tf == Indicator.EVENT:
        return {'period': target_frequency_custom}

    if tf == Indicator.ANNUAL:
        start = ((start_date + relativedelta(years=+ i)
                  ).replace(day=1)).strftime('%Y-%m-%d')
        end = ((start_date + relativedelta(years=+ j)) +
               relativedelta(days=- 1)).strftime('%Y-%m-%d')
        target_period = {'period': 'Year %s' % j,
                         'start_date': start, 'end_date': end}
    elif tf == Indicator.SEMI_ANNUAL:
        start = ((start_date + relativedelta(months=+ (i*6))
                  ).replace(day=1)).strftime('%Y-%m-%d')
        end = ((start_date + relativedelta(months=+ (j*6))) +
               relativedelta(days=- 1)).strftime('%Y-%m-%d')
        target_period = {'period': 'Semi-annual period %s' % j,
                         'start_date': start, 'end_date': end}
    elif tf == Indicator.TRI_ANNUAL:
        start = ((start_date + relativedelta(months=+ (i*4))
                  ).replace(day=1)).strftime('%Y-%m-%d')
        end = ((start_date + relativedelta(months=+ (j*4))) +
               relativedelta(days=-1)).strftime('%Y-%m-%d')
        target_period = {'period': 'Tri-annual period %s' % j,
                         'start_date': start, 'end_date': end}

    elif tf == Indicator.QUARTERLY:
        start = ((start_date + relativedelta(months=+ (i*3))
                  ).replace(day=1)).strftime('%Y-%m-%d')
        end = ((start_date + relativedelta(months=+ (j*3))) +
               relativedelta(days=-1)).strftime('%Y-%m-%d')
        target_period = {'period': 'Quarter %s' % j,
                         'start_date': start, 'end_date': end}
    elif tf == Indicator.MONTHLY:
        month = (start_date + relativedelta(months=+ i)).strftime("%B")
        year = (start_date + relativedelta(months=+ i)).strftime("%Y")
        name = month + " " + year
        start = ((start_date + relativedelta(months=+ i)
                  ).replace(day=1)).strftime('%Y-%m-%d')
        end = ((start_date + relativedelta(months=+ j)) +
               relativedelta(days=-1)).strftime('%Y-%m-%d')
        target_period = {'period': name, 'start_date': start, 'end_date': end}
    return target_period


def generate_periodic_targets(tf, start_date, num_targets,
                              target_frequency_custom=''):
    gentargets = []

    if tf == Indicator.LOP or tf == Indicator.MID_END:
        target_period = generate_periodic_target_single(
            tf, start_date, num_targets)
        return target_period

    for i in range(num_targets):
        target_period = generate_periodic_target_single(
            tf, start_date, i, target_frequency_custom)
        gentargets.append(target_period)
    return gentargets


def group_excluded(*group_names, **url):
    """
    If user is in the group passed in permission denied
    :param group_names:
    :param url:
    :return: Bool True or False is users passes test
    """
    def in_groups(u):
        if u.is_authenticated:
            if not bool(u.groups.filter(name__in=group_names)):
                return True
            raise PermissionDenied
        return False
    return user_passes_test(in_groups)


class IndicatorList(ListView):
    """
    Main Indicator Home Page,
    displays a list of Indicators Filterable by Program
    """
    model = Indicator
    template_name = 'indicators/indicator_list.html'

    def get(self, request, *args, **kwargs):

        organization = request.user.activity_user.organization
        get_programs = Program.objects.filter(organization=organization)
        # .exclude(collecteddata__isnull=True)
        get_indicators = Indicator.objects.distinct().filter(
            program__organization=organization)
        get_indicator_types = IndicatorType.objects.all()
        get_documentation = Documentation.objects.all()
        get_periodic_target = PeriodicTarget.objects.distinct().filter(
            indicator__program__organization=organization)

        program_id = int(self.kwargs['program'])
        indicator_id = int(self.kwargs['indicator'])
        type_id = int(self.kwargs['type'])

        filters = {'id__isnull': False}
        if program_id != 0:
            filters['id'] = program_id
            get_indicators = get_indicators.filter(program__in=[program_id])

        if type_id != 0:
            filters['indicator__indicator_type__id'] = type_id
            get_indicators = get_indicators.filter(indicator_type=type_id)

        if indicator_id != 0:
            filters['indicator'] = indicator_id

        programs = Program.objects.prefetch_related('indicator_set')\
            .filter(funding_status="Funded", organization=organization)\
            .filter(**filters).order_by('name')\
            .annotate(indicator_count=Count('indicator'))

        return render(request, self.template_name, {
            'get_programs': get_programs,
            'get_indicators': get_indicators,
            'get_indicator_types': get_indicator_types,
            'get_periodic_target': get_periodic_target,
            'get_documentation': DocumentationSerializer(get_documentation, many=True).data,
            'program_id': program_id,
            'indicator_id': indicator_id,
            'type_id': type_id,
            'programs': programs,
            'active': ['indicators']})


class IndicatorTarget(GView):
    def get(self, request, *args, **kwargs):
        indicator_id = int(self.kwargs['indicator_id'])
        periodic_targets = PeriodicTarget.objects.filter(indicator=indicator_id).order_by('customsort', 'create_date', 'period')
        targets = []
        for target in periodic_targets:
            targets.append({"pk": target.id, "period": str(target), "target": target.target})

        return JsonResponse({"data": targets})


def import_indicator(service=1, deserialize=True):
    """
    Import a indicators from a web service (the dig only for now)
    :param service:
    :param deserialize:
    :return:
    """
    service = ExternalService.objects.get(id=service)
    response = requests.get(service.feed_url)

    if deserialize:
        data = json.loads(response.content)  # deserialises it
    else:
        # send json data back not deserialized data
        data = response
    # debug the json data string uncomment dump and print
    # data2 = json.dumps(json_data) # json formatted string
    # print(data2)
    return data


def indicator_create(request, id=0):
    """
    Create an Indicator with a service template first, or custom.
    Step one in Inidcator creation.
    Passed on to IndicatorCreate to do the creation
    :param request:
    :param id:
    :return:
    """
    get_indicator_types = IndicatorType.objects.all()
    get_countries = Country.objects.all()
    countries = get_country(request.user)
    country_id = Country.objects.get(country=countries[0]).id
    organization = request.user.activity_user.organization
    get_programs = Program.objects.all().filter(
        funding_status="Funded", organization=organization)
    get_services = ExternalService.objects.all()
    program_id = id

    if request.method == 'POST':
        # set vars from form and get values from user

        type = IndicatorType.objects.get(indicator_type="custom")
        program = Program.objects.get(id=request.POST['program'])
        service = request.POST['services']
        level = Level.objects.all()[0]
        node_id = request.POST['service_indicator']
        sector = None
        # add a temp name for custom indicators
        name = "Temporary"
        source = None
        definition = None
        external_service_record = None

        # import recursive library for substitution
        import re

        # checkfor service indicator and update based on values
        if node_id is not None and int(node_id) != 0:
            get_imported_indicators = import_indicator(service)
            for item in get_imported_indicators:
                if item['nid'] == node_id:
                    get_sector, created = Sector.objects.get_or_create(
                        sector=item['sector'])
                    sector = get_sector
                    get_level, created = Level.objects.get_or_create(
                        name=item['level'].title())
                    level = get_level
                    name = item['title']
                    source = item['source']
                    definition = item['definition']
                    # replace HTML tags if they are in the string
                    definition = re.sub("<.*?>", "", definition)

                    get_service = ExternalService.objects.get(id=service)
                    full_url = get_service.url + "/" + item['nid']
                    external_service_record = ExternalServiceRecord(
                        record_id=item['nid'], external_service=get_service,
                        full_url=full_url)
                    external_service_record.save()
                    get_type, created = IndicatorType.objects.get_or_create(
                        indicator_type=item['type'].title())
                    type = get_type

        # save form
        new_indicator = Indicator(
            sector=sector, name=name, source=source, definition=definition,
            external_service_record=external_service_record)
        new_indicator.save()
        new_indicator.program.add(program)
        new_indicator.indicator_type.add(type)
        new_indicator.level.add(level)

        latest = new_indicator.id

        # redirect to update page
        messages.success(request, 'Success, Basic Indicator Created!')
        redirect_url = '/indicators/indicator_update/' + str(latest) + '/'
        return HttpResponseRedirect(redirect_url)

    # send the keys and vars from the json data to the template along
    # with submitted feed info and silos for new form
    return render(request, "indicators/indicator_create.html",
                  {'country_id': country_id, 'program_id': int(program_id),
                   'get_countries': get_countries,
                   'get_programs': get_programs,
                   'get_indicator_types': get_indicator_types,
                   'get_services': get_services})


class IndicatorCreate(CreateView):
    """
    Indicator Form for indicators not using a template or service indicator
    first as well as the post reciever for creating an indicator.
    Then redirect back to edit view in IndicatorUpdate.
    """
    model = Indicator
    template_name = 'indicators/indicator_form.html'

    # pre-populate parts of the form
    def get_initial(self):
        # user_profile = ActivityUser.objects.get(user=self.request.user)
        initial = {
            'program': self.kwargs['id'],
        }

        return initial

    def get_context_data(self, **kwargs):
        context = super(IndicatorCreate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['id']})
        return context

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(IndicatorCreate, self).dispatch(request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(IndicatorCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        program = Indicator.objects.all().filter(
            id=self.kwargs['pk']).values("program__id")
        kwargs['program'] = program
        return kwargs

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False, extra_tags='danger')

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Indicator Created!')
        form = ""
        return self.render_to_response(self.get_context_data(form=form))

    form_class = IndicatorForm


class PeriodicTargetView(View):
    """
    This view is responsible for generating periodic targets or deleting them
    (via POST)
    """
    model = PeriodicTarget

    def get(self, request, *args, **kwargs):
        indicator = Indicator.objects.get(
            pk=self.kwargs.get('indicator', None))
        if request.GET.get('existingTargetsOnly'):
            pts = FlatJsonSerializer().serialize(
                indicator.periodictarget_set.all().order_by('customsort',
                                                            'create_date',
                                                            'period'))
            return HttpResponse(pts)
        try:
            num_targets = int(request.GET.get('num_targets', None))
        except Exception as e:
            num_targets = PeriodicTarget.objects.filter(
                indicator=indicator).count() + 1

        pt_generated = generate_periodic_target_single(
            indicator.target_frequency, indicator.target_frequency_start,
            (num_targets-1), '')
        pt_generated_json = json.dumps(pt_generated, cls=DjangoJSONEncoder)
        return HttpResponse(pt_generated_json)

    def post(self, request, *args, **kwargs):
        indicator = Indicator.objects.get(
            pk=self.kwargs.get('indicator', None))
        deleteall = self.kwargs.get('deleteall', None)
        if deleteall == 'true':
            periodic_targets = PeriodicTarget.objects.filter(
                indicator=indicator)
            for pt in periodic_targets:
                pt.collecteddata_set.all().update(periodic_target=None)
                pt.delete()
            indicator.target_frequency = None
            indicator.target_frequency_num_periods = 1
            indicator.target_frequency_start = None
            indicator.target_frequency_custom = None
            indicator.save()
        return HttpResponse('{"status": "success", "message": '
                            '"Request processed successfully!"}')


def handle_data_collected_records(indicatr, lop, existing_target_frequency,
                                  new_target_frequency, generated_pt_ids=[]):
    # If the target_frequency is changed from LOP to something else then
    # disassociate all collected_data from the LOP periodic_target and
    # then delete the LOP periodic_target if existing_target_
    # frequency == Indicator.LOP and new_target_frequency != Indicator.LOP:
    if existing_target_frequency != new_target_frequency:
        CollectedData.objects.filter(
            indicator=indicatr).update(periodic_target=None)
        PeriodicTarget.objects.filter(indicator=indicatr).delete()

    # If the user sets target_frequency to LOP then create a LOP periodic_
    # target and associate all collected data for this indicator with this
    # single LOP periodic_target
    if existing_target_frequency != Indicator.LOP and \
            new_target_frequency == Indicator.LOP:
        lop_pt = PeriodicTarget.objects.create(
            indicator=indicatr, period=Indicator.TARGET_FREQUENCIES[0][1],
            target=lop, create_date=timezone.now())
        CollectedData.objects.filter(
            indicator=indicatr).update(periodic_target=lop_pt)

    if generated_pt_ids:
        pts = PeriodicTarget.objects.filter(
            indicator=indicatr, pk__in=generated_pt_ids)
        for pt in pts:
            CollectedData.objects.filter(
                indicator=indicatr,
                date_collected__range=[pt.start_date, pt.end_date])\
                .update(periodic_target=pt)


class IndicatorUpdate(UpdateView):
    """
    Update and Edit Indicators.
    """
    model = Indicator
    guidance = None
    template_name = 'indicators/indicator_form_tab_ui.html'
    form_class = IndicatorForm

    object = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):

        if request.method == 'GET':
            # If target_frequency is set but not targets are saved then
            # unset target_frequency too.
            indicator = self.get_object()
            if indicator.target_frequency and \
                    indicator.target_frequency != 1 and \
                    not indicator.periodictarget_set.count():
                indicator.target_frequency = None
                indicator.target_frequency_start = None
                indicator.target_frequency_num_periods = 1
                indicator.save()

        try:
            self.guidance = FormGuidance.objects.get(form="Indicator")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(IndicatorUpdate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndicatorUpdate, self).get_context_data(**kwargs)
        context.update({'id': self.kwargs['pk']})
        get_indicator = Indicator.objects.prefetch_related().filter(id=self.kwargs['pk']).first()

        # create a list of dicts from disag query
        disaggregations = [
            dict(
                disaggregation_type=item.disaggregation_type,
                id=item.id,
                labels=[
                    dict(label=label.label, id=label.id) for label in item.disaggregation_label.all()]
                )
            for item in get_indicator.disaggregation.all()
            ]

        context.update({'i_name': get_indicator.name})
        context['program_id'] = get_indicator.program.all().first().id
        context['active'] = ['indicators']
        context['disaggregations'] = json.dumps(disaggregations)
        context['periodic_targets'] = PeriodicTarget.objects\
            .filter(indicator=get_indicator)\
            .annotate(num_data=Count('collecteddata'))\
            .order_by('customsort', 'create_date', 'period')
        context['targets_sum'] = PeriodicTarget.objects.filter(
            indicator=get_indicator).aggregate(Sum('target'))['target__sum']

        # get external service data if any
        try:
            get_external_service_record = ExternalServiceRecord.objects.all()\
                .filter(
                indicator__id=self.kwargs['pk'])
        except ExternalServiceRecord.DoesNotExist:
            get_external_service_record = None
        context.update(
            {'get_external_service_record': get_external_service_record})
        if self.request.GET.get('targetsonly') == 'true':
            context['targetsonly'] = True
        elif self.request.GET.get('targetsactive') == 'true':
            context['targetsactive'] = True

        return context

    def get_initial(self):
        target_frequency_num_periods = self.get_object()\
            .target_frequency_num_periods
        if not target_frequency_num_periods:
            target_frequency_num_periods = 1
        initial = {
            'target_frequency_num_periods': target_frequency_num_periods
        }

        return initial

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(IndicatorUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        program = Indicator.objects.all().get(
            id=int(self.kwargs['pk'])).program.all()

        kwargs['program_id'] = program[0].id
        program = Indicator.objects.all().filter(
            id=self.kwargs['pk']).values_list("program__id", flat=True)
        kwargs['program'] = program
        kwargs['organization'] = self.request.user.activity_user.organization
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False, extra_tags='danger')
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form, **kwargs):
        data = self.request.POST
        indicator = self.get_object()

        # save periodic targets from the frontend
        periodic_targets_object = data.get("periodic_targets_object", None)

        if periodic_targets_object is not None:
            for target in json.loads(periodic_targets_object):
                periodic_target = PeriodicTarget(indicator=indicator, start_date=datetime.strptime(
                    target['start'], "%b %d, %Y").date(), end_date=datetime.strptime(
                    target['end'], "%b %d, %Y").date(), target=target['value'], period=target['period'])

                periodic_target.save()

        # generate the target periods and assign the values
        # for periodic_target_value in periodic_targets:

        generated_targets = []
        fields_to_watch = set(
            ['indicator_type', 'level', 'name', 'number', 'sector']
        )
        changed_fields = set(form.changed_data)
        if fields_to_watch.intersection(changed_fields):
            update_indicator_row = '1'
        else:
            update_indicator_row = '1'

        self.object = form.save()
        # periodic_targets = PeriodicTarget.objects.filter(indicator=indicatr)\
        #     .order_by('customsort','create_date', 'period')
        periodic_targets = PeriodicTarget.objects.filter(indicator=indicator).annotate(
            num_data=Count('collecteddata')).order_by('customsort', 'create_date', 'period')

        # save the disaggregation types and labels from the frontend
        disaggs = data.get("disaggregation_types", None)
        if disaggs is not None and disaggs != '':
            for disagg in json.loads(disaggs):
                if disagg.get('id', None) is None:
                    disagg_type = DisaggregationType.objects.create(
                        disaggregation_type=disagg['disaggregation_type']
                    )
                else:
                    disagg_type = DisaggregationType.objects.filter(id=int(disagg['id'])).first()
                    disagg_type.disaggregation_type = disagg['disaggregation_type']
                    disagg_type.save()

                # register disag to the indicator
                indicator.disaggregation.add(disagg_type,)

                # add disag type labels
                for label in disagg['labels']:
                    if label['id'] is None:
                        DisaggregationLabel.objects.create(
                            disaggregation_type_id=disagg_type.id,
                            label=label['label']
                        )
                    else:
                        get_label = DisaggregationLabel.objects.filter(id=int(label['id'])).first()
                        get_label.label = label['label']
                        get_label.save()

        if self.request.is_ajax():
            data = serializers.serialize('json', [self.object])
            pts = FlatJsonSerializer().serialize(periodic_targets)
            if generated_targets:
                generated_targets = json.dumps(
                    generated_targets, cls=DjangoJSONEncoder)
            else:
                generated_targets = "[]"

            targets_sum = self.get_context_data().get('targets_sum')
            if targets_sum is None:
                targets_sum = "0"
            return HttpResponse("[" + data + "," + pts + "," +
                                generated_targets + "," + str(targets_sum) +
                                "," +
                                str(update_indicator_row) + "]")
        else:
            messages.success(self.request, 'Success, Indicator Updated!')
        return redirect('/indicators/home/0/0/0/')


class IndicatorDelete(DeleteView):
    """
    Delete and Indicator
    """
    model = Indicator
    success_url = '/indicators/home/0/0/0/'

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(IndicatorDelete, self).dispatch(request, *args, **kwargs)

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form',
                       fail_silently=False, extra_tags='danger')

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()

        messages.success(self.request, 'Success, Indicator Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = IndicatorForm


def indicator_delete(request, pk):
    indicator = Indicator.objects.get(pk=int(pk))
    indicator.delete()

    return redirect('/indicators/home/0/0/0/')


class PeriodicTargetDeleteView(DeleteView):
    model = PeriodicTarget

    def delete(self, request, *args, **kwargs):
        collecteddata_count = self.get_object().collecteddata_set.count()
        if collecteddata_count > 0:
            self.get_object().collecteddata_set.all().update(
                periodic_target=None)

        # super(PeriodicTargetDeleteView).delete(request, args, kwargs)
        indicator = self.get_object().indicator
        self.get_object().delete()
        if indicator.periodictarget_set.count() == 0:
            indicator.target_frequency = None
            indicator.target_frequency_num_periods = 1
            indicator.target_frequency_start = None
            indicator.target_frequency_custom = None
            indicator.save()
        targets_sum = PeriodicTarget.objects.filter(
            indicator=indicator).aggregate(Sum('target'))['target__sum']
        return JsonResponse({"status": "success",
                             "msg": "Periodic Target deleted successfully.",
                             "targets_sum": targets_sum})


class CollectedDataAdd(GView):
    """
    Add Collected Data
    """
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))

        disaggs_list = []

        if data.get('disaggregations') == {}:
            disaggregations = None
        else:
            disaggregations = data.get('disaggregations')
            for key, value in disaggregations.items():
                item = {"value": value,
                        "disaggregation_label": key}
                disaggs_list.append(item)

        if data.get('date_collected') == "":
            date = None
        else:
            date = data.get('date_collected')

        if data.get('documentation') == "":
            documentation = None
        else:
            documentation = int(data.get('documentation'))

        collected_data = CollectedData.objects.create(
            achieved=data.get('actual', ''),
            targeted=data.get('target', ''),
            date_collected=date,
            periodic_target=PeriodicTarget.objects.filter(id=int(data.get('period', ''))).first(),
            indicator=Indicator.objects.filter(id=int(data.get('indicator', ''))).first(),
            evidence=Documentation.objects.filter(id=documentation).first(),
            program=Program.objects.filter(id=int(data.get('program', ''))).first(),
        )

        if collected_data:
            if len(disaggs_list) > 0:
                for item in disaggs_list:
                    collected_data.disaggregation_value.create(
                        value=item["value"],
                        disaggregation_label=DisaggregationLabel.objects.filter(id=int(item["disaggregation_label"])).first(),
                    )
            collecteddata_set = CollectedData.objects.filter(id=model_to_dict(collected_data)['id']).first()
            return JsonResponse({'collected_data': CollectedDataSerializer(collecteddata_set).data})
        else:
            return JsonResponse(dict(error='Failed'))


class CollectedDataEdit(GView):
    def put(self, request, *args, **kwargs):
        result_id = int(self.kwargs.get('id'))
        data = json.loads(request.body.decode('utf-8'))
        collected_data = CollectedData.objects.get(
            id=result_id
        )

        if data.get('date_collected') == "":
            date = None
        else:
            date = data.get('date_collected')

        if data.get('documentation') == "" or data.get('documentation') == None:
            documentation = None
        else:
            documentation = int(data.get('documentation'))
            evidence = Documentation.objects.filter(id=documentation).first()
            collected_data.evidence = evidence
        achieved = data.get('actual', '')

        collected_data.date_collected = date
        collected_data.achieved = achieved
        collected_data.save()

        if collected_data:
            collecteddata_set = CollectedData.objects.filter(id=result_id).first()
            return JsonResponse({'collected_data': CollectedDataSerializer(collecteddata_set).data})
        else:
            return JsonResponse(dict(error='Failed'))


class CollectedDataDeleteVue(GView):
    def delete(self, request, *args, **kwargs):
        result_id = int(self.kwargs.get('id'))
        result = CollectedData.objects.get(
            id=int(result_id)
        )
        result.delete()

        try:
            CollectedData.objects.get(id=int(result_id))
            return JsonResponse(dict(error='Failed'))

        except CollectedData.DoesNotExist:

            return JsonResponse(dict(success=True))


class CollectedDataCreate(CreateView):
    """
    CollectedData Form
    """
    model = CollectedData
    guidance = None
    form_class = CollectedDataForm

    def get_template_names(self):
        if self.request.is_ajax():
            return 'indicators/collecteddata_form_modal.html'
        return 'indicators/collecteddata_form.html'

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="CollectedData")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(CollectedDataCreate, self)\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CollectedDataCreate, self).get_context_data(**kwargs)
        dissags_list = Indicator.objects.filter(pk=int(self.kwargs['indicator']))\
            .values_list('disaggregation__id', flat=True).first()
        try:
            get_disaggregation_label = DisaggregationLabel.objects.filter(
                disaggregation_type__id__in=dissags_list if dissags_list is not None else [])
            get_disaggregation_label_standard = \
                DisaggregationLabel.objects.all().filter(
                    disaggregation_type__standard=True)
        except DisaggregationLabel.DoesNotExist:
            get_disaggregation_label_standard = None
            get_disaggregation_label = None

        # set values to None so the form doesn't display empty fields
        # for previous entries
        get_disaggregation_value = None
        indicator = Indicator.objects.get(pk=int(self.kwargs.get('indicator')))

        context.update({'get_disaggregation_value': get_disaggregation_value})
        context.update({'get_disaggregation_label': get_disaggregation_label})
        context.update({
            'get_disaggregation_label_standard':
                get_disaggregation_label_standard})
        context.update({'indicator_id': self.kwargs['indicator']})
        context.update({'indicator': indicator})
        context.update(
            {'program_id': self.kwargs['program'], 'active': ['indicators']})

        return context

    def get_initial(self):
        initial = {
            'indicator': self.kwargs['indicator'],
            'program': self.kwargs['program'],
        }

        return initial

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(CollectedDataCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['program'] = self.kwargs['program']
        kwargs['indicator'] = self.kwargs['indicator']
        kwargs['activity_table'] = None

        return kwargs

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form',
                       fail_silently=False, extra_tags='danger')

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        dissags_list = Indicator.objects.filter(pk=int(self.kwargs['indicator']))\
            .values_list('disaggregation__id', flat=True).first()
        disaggregation_labels = DisaggregationLabel.objects.filter(
            Q(disaggregation_type__id__in=dissags_list if dissags_list is not None else []) |
            Q(disaggregation_type__standard=True))

        # update the count with the value of Table unique count
        if form.instance.update_count_activity_table and \
                form.instance.activity_table:
            try:
                get_table = ActivityTable.objects.get(
                    id=self.request.POST['activity_table'])
            except DisaggregationLabel.DoesNotExist:
                get_table = None
            if get_table:
                # if there is a trailing slash, remove it since TT api
                # does not like it.
                url = get_table.url if get_table.url[-1:] != "/" \
                    else get_table.url[:-1]
                url = url if url[-5:] != "/data" else url[:-5]
                count = get_table_count(url, get_table.table_id)
            else:
                count = 0
            form.instance.achieved = count
            if self.kwargs['indicator'] != 0:
                form.instance.indicator_id = int(self.kwargs['indicator'])

        new = form.save()

        process_disaggregation = False

        for label in disaggregation_labels:
            if process_disaggregation:
                break
            for k, v in self.request.POST.iteritems():
                if k == str(label.id) and len(v) > 0:
                    process_disaggregation = True
                    break

        if process_disaggregation:
            for label in disaggregation_labels:
                for k, v in self.request.POST.iteritems():
                    if k == str(label.id):
                        save = new.disaggregation_value.create(
                            disaggregation_label=label, value=v)
                        new.disaggregation_value.add(save.id)
            process_disaggregation = False

        if self.request.is_ajax():
            data = serializers.serialize('json', [new])
            return HttpResponse(data)

        messages.success(self.request, 'Success, Data Created!')

        redirect_url = '/indicators/home/0/0/0/#hidden-' + \
            str(self.kwargs['program'])
        return HttpResponseRedirect(redirect_url)


class CollectedDataUpdate(UpdateView):
    """
    CollectedData Form
    """
    model = CollectedData
    guidance = None

    def get_template_names(self):
        if self.request.is_ajax():
            return 'indicators/collecteddata_form_modal.html'
        return 'indicators/collecteddata_form.html'

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="CollectedData")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(CollectedDataUpdate, self)\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CollectedDataUpdate, self).get_context_data(**kwargs)
        # get the indicator_id for the collected data
        get_indicator = CollectedData.objects.get(id=self.kwargs['pk'])

        try:
            if get_indicator.indicator is not None:
                get_disaggregation_label = DisaggregationLabel.objects.all()\
                    .filter(
                    disaggregation_type__indicator__id=get_indicator.indicator.id)
            else:
                get_disaggregation_label = None

            get_disaggregation_label_standard = \
                DisaggregationLabel.objects.all().filter(
                    disaggregation_type__standard=True)

        except DisaggregationLabel.DoesNotExist:
            get_disaggregation_label = None
            get_disaggregation_label_standard = None

        try:
            get_disaggregation_value = DisaggregationValue.objects.all()\
                .filter(collecteddata=self.kwargs['pk'])\
                .exclude(
                disaggregation_label__disaggregation_type__standard=True)
            get_disaggregation_value_standard = \
                DisaggregationValue.objects.all().filter(
                    collecteddata=self.kwargs['pk'])\
                .filter(
                    disaggregation_label__disaggregation_type__standard=True)
        except DisaggregationLabel.DoesNotExist:
            get_disaggregation_value = None
            get_disaggregation_value_standard = None

        context.update({
            'get_disaggregation_label_standard':
                get_disaggregation_label_standard})
        context.update(
            {'get_disaggregation_value_standard':
                get_disaggregation_value_standard})
        context.update({'get_disaggregation_value': get_disaggregation_value})
        context.update({'get_disaggregation_label': get_disaggregation_label})
        context.update({'id': self.kwargs['pk']})
        context.update({'indicator_id': get_indicator.indicator_id})
        context.update({'indicator': get_indicator})

        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False, extra_tags='danger')
        return self.render_to_response(self.get_context_data(form=form))

    # add the request to the kwargs
    def get_form_kwargs(self):
        get_data = CollectedData.objects.get(id=self.kwargs['pk'])
        kwargs = super(CollectedDataUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['program'] = get_data.program
        kwargs['indicator'] = get_data.indicator
        if get_data.activity_table:
            kwargs['activity_table'] = get_data.activity_table.id
        else:
            kwargs['activity_table'] = None
        return kwargs

    def form_valid(self, form):

        get_collected_data = CollectedData.objects.get(id=self.kwargs['pk'])
        get_disaggregation_label = DisaggregationLabel.objects.all()\
            .filter(
            Q(disaggregation_type__indicator__id=self.request.POST.get('indicator')) |
            Q(disaggregation_type__standard=True)).distinct()

        get_indicator = CollectedData.objects.get(id=self.kwargs['pk'])

        # update the count with the value of Table unique count
        if form.instance.update_count_activity_table and \
                form.instance.activity_table:
            try:
                get_table = ActivityTable.objects.get(
                    id=self.request.POST['activity_table'])
            except ActivityTable.DoesNotExist:
                get_table = None
            if get_table:
                # if there is a trailing slash, remove it since TT api
                # does not like it.
                url = get_table.url if get_table.url[-1:] != "/" \
                    else get_table.url[:-1]
                url = url if url[-5:] != "/data" else url[:-5]
                count = get_table_count(url, get_table.table_id)
            else:
                count = 0
            form.instance.achieved = count

        # save the form then update manytomany relationships
        form.save()

        # Insert or update disagg values
        for label in get_disaggregation_label:
            for key, value in self.request.POST.iteritems():
                if key == str(label.id):
                    value_to_insert = value
                    save = get_collected_data.disaggregation_value.create(
                        disaggregation_label=label, value=value_to_insert)
                    get_collected_data.disaggregation_value.add(save.id)

        if self.request.is_ajax():
            data = serializers.serialize('json', [self.object])
            return HttpResponse(data)

        messages.success(self.request, 'Success, Data Updated!')

        redirect_url = '/indicators/home/0/0/0/'
        return HttpResponseRedirect(redirect_url)

    form_class = CollectedDataForm


class DisaggregationTypeDeleteView(DeleteView):
    model = DisaggregationType

    def delete(self, request, *args, **kwargs):
        try:
            self.get_object().delete()
            return JsonResponse(dict(status=204))

        except Exception as e:
            return JsonResponse(dict(status=400))


class DisaggregationLabelDeleteView(DeleteView):
    model = DisaggregationLabel

    def delete(self, request, *args, **kwargs):
        try:
            self.get_object().delete()
            return JsonResponse(dict(status=204))

        except Exception as e:
            return JsonResponse(dict(status=400))


class CollectedDataDelete(DeleteView):
    """
    CollectedData Delete
    """
    model = CollectedData
    success_url = '/indicators/home/0/0/0/'

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        return super(CollectedDataDelete, self)\
            .dispatch(request, *args, **kwargs)


def get_table_count(url, table_id):
    """
    Count the number of rowns in a ActivityTable
    :param url:
    :param table_id: The ActivityTable ID to update count from and return
    :return: count : count of rows from ActivityTable
    """
    token = ActivitySites.objects.get(site_id=1)
    if token.activity_tables_token:
        headers = {'content-type': 'application/json',
                   'Authorization': 'Token ' + token.activity_tables_token}
    else:
        headers = {'content-type': 'application/json'}
        print("Token Not Found")

    response = requests.get(url, headers=headers, verify=True)
    data = json.loads(response.content)
    count = None
    try:
        count = data['data_count']
        ActivityTable.objects.filter(table_id=table_id)\
            .update(unique_count=count)
    except KeyError:
        pass

    return count


def merge_two_dicts(x, y):
    """
    Given two dictionary Items, merge them into a new dict as a shallow copy.
    :param x: Dict 1
    :param y: Dict 2
    :return: Merge of the 2 Dicts
    """
    z = x.copy()
    z.update(y)
    return z


def collecteddata_import(request):
    """
    Import collected data from Activity Tables
    :param request:
    :return:
    """
    owner = request.user
    # get the activitytables URL and token from the sites object
    service = ActivitySites.objects.get(site_id=1)

    # add filter to get just the users tables only
    user_filter_url = service.activity_tables_url + \
        "&owner__username=" + str(owner)
    shared_filter_url = service.activity_tables_url + \
        "&shared__username=" + str(owner)

    user_json = get_table(user_filter_url)
    shared_json = get_table(shared_filter_url)

    if type(shared_json) is not dict:
        data = user_json + shared_json
    else:
        data = user_json

    if request.method == 'POST':
        id = request.POST['service_table']
        filter_url = service.activity_tables_url + "&id=" + id

        data = get_table(filter_url)

        # Get Data Info
        for item in data:
            name = item['name']
            url = item['data']
            remote_owner = item['owner']['username']

        # send table ID to count items in data
        count = get_table_count(url, id)

        # get the users country
        countries = get_country(request.user)
        check_for_existence = ActivityTable.objects.all()\
            .filter(name=name, owner=owner)
        if check_for_existence:
            result = check_for_existence[0].id
        else:
            create_table = ActivityTable.objects.create(
                name=name, owner=owner, remote_owner=remote_owner,
                table_id=id, url=url, unique_count=count)
            create_table.country.add(countries[0].id)
            create_table.save()
            result = create_table.id

        # send result back as json
        message = result
        return HttpResponse(json.dumps(message),
                            content_type='application/json')

    # send the keys and vars from the json data to the template along
    # with submitted feed info and silos for new form
    return render(request, "indicators/collecteddata_import.html",
                  {'get_tables': data})


def service_json(request, service):
    """
    For populating service indicators in dropdown
    :param service: The remote data service
    :return: JSON object of the indicators from the service
    """
    service_indicators = import_indicator(service, deserialize=False)
    return HttpResponse(service_indicators, content_type="application/json")


def collected_data_json(AjaxableResponseMixin, indicator, program):
    ind = Indicator.objects.get(pk=indicator)

    periodic_targets = PeriodicTarget.objects.filter(
        indicator=indicator).prefetch_related('collecteddata_set')\
        .order_by('customsort')

    collected_data_without_periodic_targets = CollectedData.objects.filter(
        indicator=indicator, periodic_target__isnull=True)

    collected_sum = CollectedData.objects\
        .select_related('periodic_target')\
        .filter(indicator=indicator)\
        .aggregate(Sum('periodic_target__target'), Sum('achieved'))

    return JsonResponse({
        'periodictargets': PeriodicTargetSerializer(periodic_targets, many=True).data,
        'collecteddata_without_periodictargets': CollectedDataSerializer(collected_data_without_periodic_targets, many=True).data,
        'collected_sum': collected_sum,
        'indicator': IndicatorSerializer(ind).data,
        'program_id': program
    })


def program_indicators_json(AjaxableResponseMixin, program, indicator, type):
    template_name = 'indicators/program_indicators_table.html'

    q = {'program__id__isnull': False}
    if int(program) != 0:
        q['program__id'] = program

    if int(type) != 0:
        q['indicator_type__id'] = type

    if int(indicator) != 0:
        q['id'] = indicator

        #
    indicators = Indicator.objects\
        .select_related('sector')\
        .prefetch_related('collecteddata_set', 'indicator_type', 'level',
                          'periodictarget_set')\
        .filter(**q)\
        .annotate(data_count=Count('collecteddata'),
                  levelmin=Min('level__id'))\
        .order_by('levelmin', 'number')

    return render_to_response(template_name, {'indicators': indicators,
                                              'program_id': program})


# def tool(request):
#     """
#     Placeholder for Indicator planning Tool TBD
#     :param request:
#     :return:
#     """
#     return render(request, 'indicators/tool.html')


# REPORT VIEWS
def indicator_report(request, program=0, indicator=0, type=0):
    organization = request.user.activity_user.organization
    get_programs = Program.objects.filter(
        funding_status="Funded", organization=organization)
    get_indicator_types = IndicatorType.objects.all()

    filters = {}
    if int(program) != 0:
        filters['program__id'] = program
    if int(type) != 0:
        filters['indicator_type'] = type
    if int(indicator) != 0:
        filters['id'] = indicator

    filters['program__organization'] = organization

    indicator_data = Indicator.objects.filter(**filters)\
        .prefetch_related('sector')\
        .select_related('program', 'external_service_record', 'indicator_type',
                        'disaggregation', 'reporting_frequency')\
        .values(
        'id', 'program__name', 'baseline', 'level__name', 'lop_target',
        'program__id', 'external_service_record__external_service__name',
        'key_performance_indicator', 'name', 'indicator_type__id',
        'indicator_type__indicator_type', 'sector__sector',
        'disaggregation__disaggregation_type', 'means_of_verification',
        'data_collection_method', 'reporting_frequency__frequency',
        'create_date', 'edit_date', 'source', 'method_of_analysis')

    data = json.dumps(list(indicator_data), cls=DjangoJSONEncoder)

    # send the keys and vars from the json data to the template along
    # with submitted feed info and silos for new form
    return render(request, "indicators/report.html", {
                  'program': program,
                  'get_programs': get_programs,
                  'get_indicator_types': get_indicator_types,
                  'get_indicators': indicator_data,
                  'data': data})


class IndicatorReport(View, AjaxableResponseMixin):
    def get(self, request, *args, **kwargs):

        organization = request.user.activity_user.organization
        # get_programs = Program.objects.all().filter(
        #      funding_status="Funded", organization=organization)

        # get_indicator_types = IndicatorType.objects.all()

        program = int(self.kwargs['program'])
        indicator = int(self.kwargs['indicator'])
        type = int(self.kwargs['type'])

        filters = {}
        if program != 0:
            filters['program__id'] = program
        if type != 0:
            filters['indicator_type'] = type
        if indicator != 0:
            filters['id'] = indicator
        if program == 0 and type == 0:
            filters['program__organization'] = organization

        get_indicators = Indicator.objects.filter(**filters)\
            .prefetch_related('sector')\
            .select_related('program', 'external_service_record',
                            'indicator_type', 'disaggregation',
                            'reporting_frequency')\
            .values('id', 'program__name', 'baseline', 'level__name',
                    'lop_target', 'program__id',
                    'external_service_record__external_service__name',
                    'key_performance_indicator', 'name',
                    'indicator_type__indicator_type',
                    'sector__sector', 'disaggregation__disaggregation_type',
                    'means_of_verification', 'data_collection_method',
                    'reporting_frequency__frequency', 'create_date',
                    'edit_date', 'source', 'method_of_analysis')

        q = request.GET.get('search', None)
        if q:
            get_indicators = get_indicators.filter(
                Q(indicator_type__indicator_type__contains=q) |
                Q(name__contains=q) |
                Q(number__contains=q) |
                Q(number__contains=q) |
                Q(sector__sector__contains=q) |
                Q(definition__contains=q)
            )

        get_indicators = json.dumps(list(get_indicators),
                                    cls=DjangoJSONEncoder)

        return JsonResponse(get_indicators, safe=False)


def program_indicator_report(request, program=0):
    """
    This is the GRID report or indicator plan for a program.
    Shows a simple list of indicators sorted by level
    and number. Lives in the "Indicator" home page as a link.
    URL: indicators/program_report/[program_id]/
    :param request:
    :param program:
    :return:
    """
    program = int(program)
    organization = request.user.activity_user.organization
    get_programs = Program.objects.all().filter(
        funding_status="Funded", organization=organization)
    get_indicators = Indicator.objects.all().filter(
        program__id=program).select_related().order_by('level', 'number')
    get_program = Program.objects.get(id=program)

    get_indicator_types = IndicatorType.objects.all()

    if request.method == "GET" and "search" in request.GET:
        # list1 = list()
        # for obj in filtered:
        #    list1.append(obj)
        get_indicators = Indicator.objects.all().filter(
            Q(indicator_type__icontains=request.GET["search"]) |
            Q(name__icontains=request.GET["search"]) |
            Q(number__icontains=request.GET["search"]) |
            Q(definition__startswith=request.GET["search"])
        ).filter(program__id=program).select_related()\
            .order_by('level', 'number')

    # send the keys and vars from the json data to the template along with
    # submitted feed info and silos for new form
    return render(request, "indicators/grid_report.html",
                  {'get_indicators': get_indicators,
                   'get_programs': get_programs,
                   'get_program': get_program, 'form': FilterForm(),
                   'helper': FilterForm.helper,
                   'get_indicator_types': get_indicator_types})


def indicator_data_report(request, id=0, program=0, type=0):
    countries = request.user.activity_user.countries.all()
    organization = request.user.activity_user.organization
    get_programs = Program.objects.all().filter(
        funding_status="Funded", organization=organization)
    get_indicators = Indicator.objects.select_related().filter(
        program__organization=organization)
    get_indicator_types = IndicatorType.objects.all()
    indicator_name = None
    program_name = None
    type_name = None
    q = {'indicator__id__isnull': False}

    get_site_profile = SiteProfile.objects\
        .filter(projectagreement__program__organization=organization)\
        .select_related('country', 'district', 'province')

    if int(id) != 0:
        indicator_name = Indicator.objects.get(id=id).name
        q['indicator__id'] = id
    else:
        q['indicator__program__organization'] = organization

    if int(program) != 0:
        get_site_profile = SiteProfile.objects\
            .filter(projectagreement__program__id=program)\
            .select_related('country', 'district', 'province')
        program_name = Program.objects.get(id=program).name
        q = {'program__id': program}
        get_indicators = Indicator.objects.select_related()\
            .filter(program=program)

    if int(type) != 0:
        type_name = IndicatorType.objects.get(id=type).indicator_type
        q = {'indicator__indicator_type__id': type}

    if request.method == "GET" and "search" in request.GET:
        queryset = CollectedData.objects.filter(**q)\
            .filter(
            Q(agreement__project_name__contains=request.GET["search"]) |
            Q(description__icontains=request.GET["search"]) |
            Q(indicator__name__contains=request.GET["search"]))\
            .select_related()
    else:
        queryset = CollectedData.objects.all().filter(**q).select_related()

    # pass query to table and configure
    table = IndicatorDataTable(queryset)
    table.paginate(page=request.GET.get('page', 1), per_page=20)

    RequestConfig(request).configure(table)

    filters = {'status': 1, 'country__in': countries}
    get_site_profile_indicator = SiteProfile.objects\
        .select_related('country', 'district', 'province')\
        .prefetch_related('collecteddata_set')\
        .filter(**filters)

    # send the keys and vars from the json data to the template along
    # with submitted feed info and silos for new form
    return render(request, "indicators/data_report.html", {
        'get_quantitative_data': queryset,
        'countries': countries,
        'get_site_profile': get_site_profile,
        'get_programs': get_programs,
        'get_indicators': get_indicators,
        'get_indicator_types': get_indicator_types,
        'form': FilterForm(),
        'helper': FilterForm.helper,
        'id': id,
        'program': program,
        'type': type,
        'indicator': id,
        'indicator_name': indicator_name,
        'type_name': type_name,
        'program_name': program_name,
        'get_site_profile_indicator': get_site_profile_indicator,
    })


class IndicatorReportData(View, AjaxableResponseMixin):
    """
    This is the Indicator Visual report data, returns a json object of
    report data to be displayed in the table report
    URL: indicators/report_data/[id]/[program]/
    :param request:
    :param id: Indicator ID
    :param program: Program ID
    :param type: Type ID
    :return: json dataset
    """

    def get(self, request, program, type, id):
        q = {'program__id__isnull': False}
        # if we have a program filter active
        if int(program) != 0:
            q = {
                'program__id': program,
            }
        # if we have an indicator type active
        if int(type) != 0:
            r = {
                'indicator_type__id': type,
            }
            q.update(r)
        # if we have an indicator id append it to the query filter
        if int(id) != 0:
            s = {
                'id': id,
            }
            q.update(s)

        organization = request.user.activity_user.organization

        indicator = Indicator.objects.filter(
            program__organization=organization)\
            .filter(**q).values(
            'id', 'program__name', 'baseline', 'level__name', 'lop_target',
            'program__id', 'external_service_record__external_service__name',
            'key_performance_indicator', 'name', 'indicator_type__id',
            'indicator_type__indicator_type',
            'sector__sector').order_by('create_date')

        indicator_count = Indicator.objects.all()\
            .filter(program__organization=organization).filter(**q).filter(
            collecteddata__isnull=True).distinct().count()
        indicator_data_count = Indicator.objects.all()\
            .filter(program__organization=organization).filter(**q).filter(
            collecteddata__isnull=False).distinct().count()

        indicator_serialized = json.dumps(list(indicator))

        final_dict = {
            'indicator': indicator_serialized,
            'indicator_count': indicator_count,
            'data_count': indicator_data_count
        }

        if request.GET.get('export'):
            indicator_export = Indicator.objects.all().filter(**q)
            dataset = IndicatorResource().export(indicator_export)
            response = HttpResponse(
                dataset.csv, content_type='application/ms-excel')
            response['Content-Disposition'] = \
                'attachment; filename=indicator_data.csv'
            return response

        return JsonResponse(final_dict, safe=False)


class CollectedDataReportData(View, AjaxableResponseMixin):
    """
    This is the Collected Data reports data in JSON format for a
    specific indicator
    URL: indicators/collectedaata/[id]/
    :param request:
    :param indicator: Indicator ID
    :return: json dataset
    """

    def get(self, request, *args, **kwargs):

        organization = request.user.activity_user.organization

        program = kwargs['program']
        indicator = kwargs['indicator']
        type = kwargs['type']

        q = {'program__id__isnull': False}
        # if we have a program filter active
        if int(program) != 0:
            q = {
                'indicator__program__id': program,
            }
        # if we have an indicator type active
        if int(type) != 0:
            r = {
                'indicator__indicator_type__id': type,
            }
            q.update(r)
        # if we have an indicator id append it to the query filter
        if int(indicator) != 0:
            s = {
                'indicator__id': indicator,
            }
            q.update(s)

        get_collected_data = CollectedData.objects.all()\
            .select_related('periodic_target').prefetch_related(
            'evidence', 'indicator', 'program',
            'indicator__objectives',
            'indicator__strategic_objectives')\
            .filter(program__organization=organization).filter(
            **q).order_by('indicator__program__name', 'indicator__number')\
            .values(
            'id', 'indicator__id', 'indicator__name',
            'indicator__program__id', 'indicator__program__name',
            'indicator__indicator_type__indicator_type',
            'indicator__indicator_type__id', 'indicator__level__name',
            'indicator__sector__sector', 'date_collected',
            'indicator__baseline', 'indicator__lop_target',
            'indicator__key_performance_indicator',
            'indicator__external_service_record__external_service__name',
            'evidence', 'activity_table', 'periodic_target', 'achieved')

        collected_sum = CollectedData.objects\
            .select_related('periodic_target')\
            .filter(program__organization=organization).filter(**q)\
            .aggregate(Sum('periodic_target__target'), Sum('achieved'))

        # datetime encoding breaks without using this
        from django.core.serializers.json import DjangoJSONEncoder
        collected_serialized = json.dumps(
            list(get_collected_data), cls=DjangoJSONEncoder)

        final_dict = {
            'collected': collected_serialized,
            'collected_sum': collected_sum
        }

        return JsonResponse(final_dict, safe=False)


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class DisaggregationReportMixin(object):
    def get_context_data(self, **kwargs):
        context = super(DisaggregationReportMixin,
                        self).get_context_data(**kwargs)

        organization = self.request.user.activity_user.organization
        programs = Program.objects.filter(
            funding_status="Funded", organization=organization)
        indicators = Indicator.objects.filter(
            program__organization=organization)

        program_id = int(kwargs.get('program', 0))
        program_selected = None
        if program_id:
            program_selected = Program.objects.filter(id=program_id).first()
            if program_selected.indicator_set.count() > 0:
                indicators = indicators.filter(program=program_id)

        disagg_query = \
            "SELECT i.id AS IndicatorID, dt.disaggregation_type AS DType, "\
            "l.customsort AS customsort, l.label AS Disaggregation, " \
            "SUM(CAST(dv.value as decimal)) AS Actuals "\
            "FROM indicators_collecteddata_disaggregation_value AS cdv "\
            "INNER JOIN indicators_collecteddata AS c ON " \
            "c.id = cdv.collecteddata_id "\
            "INNER JOIN indicators_indicator AS i ON i.id = c.indicator_id "\
            "INNER JOIN indicators_indicator_program AS ip ON " \
            "ip.indicator_id = i.id "\
            "INNER JOIN workflow_program AS p ON p.id = ip.program_id "\
            "INNER JOIN indicators_disaggregationvalue AS dv ON " \
            "dv.id = cdv.disaggregationvalue_id "\
            "INNER JOIN indicators_disaggregationlabel AS l ON " \
            "l.id = dv.disaggregation_label_id "\
            "INNER JOIN indicators_disaggregationtype AS dt ON " \
            "dt.id = l.disaggregation_type_id "\
            "WHERE p.id = %s "\
            "GROUP BY IndicatorID, DType, customsort, Disaggregation "\
            "ORDER BY IndicatorID, DType, customsort, Disaggregation;" \
            % program_id
        cursor = connection.cursor()
        cursor.execute(disagg_query)
        disdata = dictfetchall(cursor)

        indicator_query = \
            "SELECT DISTINCT p.id as PID, i.id AS IndicatorID, i.number " \
            "AS INumber, "\
            "i.name AS Indicator, i.lop_target AS LOP_Target, " \
            "SUM(cd.achieved) AS Overall "\
            "FROM indicators_indicator AS i "\
            "INNER JOIN indicators_indicator_program AS ip ON " \
            "ip.indicator_id = i.id "\
            "INNER JOIN workflow_program AS p ON p.id = ip.program_id "\
            "LEFT OUTER JOIN indicators_collecteddata AS cd ON " \
            "i.id = cd.indicator_id "\
            "WHERE p.id = %s "\
            "GROUP BY PID, IndicatorID "\
            "ORDER BY Indicator; " % program_id
        cursor.execute(indicator_query)
        idata = dictfetchall(cursor)

        for indicator in idata:
            indicator["disdata"] = []
            for i, dis in enumerate(disdata):
                if dis['IndicatorID'] == indicator['IndicatorID']:
                    indicator["disdata"].append(disdata[i])

        context['program_id'] = program_id
        context['data'] = idata
        context['get_programs'] = programs
        context['get_indicators'] = indicators
        context['program_selected'] = program_selected
        return context


class DisaggregationReport(DisaggregationReportMixin, TemplateView):
    template_name = 'indicators/disaggregation_report.html'

    def get_context_data(self, **kwargs):
        context = super(DisaggregationReport, self).get_context_data(**kwargs)
        context['disaggregationprint_button'] = True
        return context


class DisaggregationPrint(DisaggregationReportMixin, TemplateView):
    template_name = 'indicators/disaggregation_print.html'

    def get(self, request, *args, **kwargs):
        context = super(DisaggregationPrint, self).get_context_data(**kwargs)
        hmtl_string = render(
            request, self.template_name, {
                'data': context['data'],
                'program_selected': context['program_selected']})
        pdffile = HTML(string=hmtl_string.content)

        result = pdffile.write_pdf(stylesheets=[CSS(
            string='@page {\
                size: letter; margin: 1cm;\
                @bottom-right{\
                    content: "Page " counter(page) " of " counter(pages);\
                };\
            }'
        )])
        res = HttpResponse(result, content_type='application/pdf')
        res['Content-Disposition'] = \
            'attachment; filename=indicators_disaggregation_report.pdf'
        res['Content-Transfer-Encoding'] = 'binary'
        return res


class TVAPrint(TemplateView):
    template_name = 'indicators/tva_print.html'

    def get(self, request, *args, **kwargs):
        program = Program.objects.filter(
            id=kwargs.get('program', None)).first()
        indicators = Indicator.objects\
            .select_related('sector')\
            .prefetch_related('indicator_type', 'level', 'program')\
            .filter(program=program)\
            .annotate(actuals=Sum('collecteddata__achieved'))

        hmtl_string = render(request, 'indicators/tva_print.html',
                             {'data': indicators, 'program': program})
        pdffile = HTML(string=hmtl_string.content)
        result = pdffile.write_pdf(stylesheets=[CSS(
            string='@page {\
                size: letter; margin: 1cm;\
                @bottom-right{\
                    content: "Page " counter(page) " of " counter(pages);\
                };\
            }'
        )])
        res = HttpResponse(result, content_type='application/pdf')
        res['Content-Disposition'] = 'attachment; filename=tva.pdf'
        res['Content-Transfer-Encoding'] = 'binary'
        """
        with tempfile.NamedTemporaryFile(delete=True) as output:
            output.write(result)
            output.flush()
            output = open(output.name, 'r')
            res.write(output.read())
        """
        """
        # Create the PDF object, using the response object as its "file."
        p = canvas.Canvas(res)
        p.drawString(100, 100, 'hello world!')
        p.showPage()
        p.save()
        """
        return res


class TVAReport(TemplateView):
    template_name = 'indicators/tva_report.html'

    def get_context_data(self, **kwargs):
        context = super(TVAReport, self).get_context_data(**kwargs)
        organization = self.request.user.activity_user.organization
        filters = {'program__organization': organization}
        program = Program.objects.filter(
            id=kwargs.get('program', None)).first()
        indicator_type = IndicatorType.objects.filter(
            id=kwargs.get('type', None)).first()
        indicator = Indicator.objects.filter(
            id=kwargs.get('indicator', None)).first()

        if program:
            filters['program'] = program.pk
        if indicator_type:
            filters['indicator__indicator_type__id'] = indicator_type.pk
        if indicator:
            filters['indicator'] = indicator.pk

        indicators = Indicator.objects\
            .select_related('sector')\
            .prefetch_related('indicator_type', 'level', 'program')\
            .filter(**filters)\
            .annotate(actuals=Sum('collecteddata__achieved'))
        context['data'] = indicators
        context['get_indicators'] = Indicator.objects.filter(
            program__organization=organization)
        context['get_programs'] = Program.objects.filter(
            funding_status="Funded", organization=organization)
        context['get_indicator_types'] = IndicatorType.objects.all()
        context['program'] = program
        context['export_to_pdf_url'] = True
        return context


class CollectedDataList(ListView):
    """
    This is the Indicator CollectedData report for each indicator and program.
    Displays a list collected data entries
    and sums it at the bottom.  Lives in the "Reports" navigation.
    URL: indicators/data/[id]/[program]/[type]
    :param request:
    :param indicator: Indicator ID
    :param program: Program ID
    :param type: Type ID
    :return:
    """
    model = CollectedData
    template_name = 'indicators/collecteddata_list.html'

    def get(self, request, *args, **kwargs):

        organization = request.user.activity_user.organization
        get_programs = Program.objects.all().filter(
            funding_status="Funded", organization=organization)
        get_indicators = Indicator.objects.all()\
            .filter(program__organization=organization).exclude(
            collecteddata__isnull=True)
        get_indicator_types = IndicatorType.objects.all()
        program = self.kwargs['program']
        indicator = self.kwargs['indicator']
        type = self.kwargs['type']
        indicator_name = ""
        type_name = ""
        program_name = ""

        q = {'program__id__isnull': False}
        # if we have a program filter active
        if int(program) != 0:
            q = {
                'program__id': program,
            }
            # redress the indicator list based on program
            get_indicators = Indicator.objects.select_related()\
                .filter(program=program)
            program_name = Program.objects.get(id=program)
        # if we have an indicator type active
        if int(type) != 0:
            r = {
                'indicator__indicator_type__id': type,
            }
            q.update(r)
            # redress the indicator list based on type
            get_indicators = Indicator.objects.select_related()\
                .filter(indicator_type__id=type)
            type_name = IndicatorType.objects.get(id=type).indicator_type
        # if we have an indicator id append it to the query filter
        if int(indicator) != 0:
            s = {
                'indicator': indicator,
            }
            q.update(s)
            indicator_name = Indicator.objects.get(id=indicator)

        indicators = CollectedData.objects.all()\
            .select_related('periodic_target')\
            .prefetch_related('evidence', 'indicator', 'program',
                              'indicator__objectives',
                              'indicator__strategic_objectives').filter(
            program__organization=organization).filter(
            **q).order_by(
            'indicator__program__name',
            'indicator__number').values(
            'indicator__id', 'indicator__name',
            'indicator__program__name',
            'indicator__indicator_type__indicator_type',
            'indicator__level__name', 'indicator__sector__sector',
            'date_collected', 'indicator__baseline',
            'indicator__lop_target', 'indicator__key_performance_indicator',
            'indicator__external_service_record__external_service__name',
            'evidence', 'activity_table', 'periodic_target', 'achieved')

        if self.request.GET.get('export'):
            dataset = CollectedDataResource().export(indicators)
            response = HttpResponse(
                dataset.csv, content_type='application/ms-excel')
            response['Content-Disposition'] = \
                'attachment; filename=indicator_data.csv'
            return response

        return render(request, self.template_name, {
            'indicators': indicators,
            'get_programs': get_programs,
            'get_indicator_types': get_indicator_types,
            'get_indicators': get_indicators,
            'type': type,
            'filter_program': program_name,
            'filter_indicator': indicator_name,
            'indicator': indicator,
            'program': program,
            'indicator_name': indicator_name,
            'program_name': program_name,
            'type_name': type_name,
        })


class IndicatorExport(View):
    """
    Export all indicators to a CSV file
    """

    def get(self, request, *args, **kwargs):
        if int(kwargs['id']) == 0:
            del kwargs['id']
        if int(kwargs['indicator_type']) == 0:
            del kwargs['indicator_type']
        if int(kwargs['program']) == 0:
            del kwargs['program']

        organization = request.user.activity_user.organization

        queryset = Indicator.objects.filter(
            **kwargs).filter(program__organization=organization)

        indicator = IndicatorResource().export(queryset)
        response = HttpResponse(
            indicator.csv, content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=indicator.csv'
        return response


class IndicatorDataExport(View):
    """
    Export all indicators to a CSV file
    """

    def get(self, request, *args, **kwargs):

        if int(kwargs['indicator']) == 0:
            del kwargs['indicator']
        if int(kwargs['program']) == 0:
            del kwargs['program']
        if int(kwargs['type']) == 0:
            del kwargs['type']
        else:
            kwargs['indicator__indicator_type__id'] = kwargs['type']
            del kwargs['type']

        organization = request.user.activity_user.organization

        queryset = CollectedData.objects.filter(
            **kwargs).filter(indicator__program__organization=organization)
        dataset = CollectedDataResource().export(queryset)
        response = HttpResponse(
            dataset.csv, content_type='application/ms-excel')
        response['Content-Disposition'] = \
            'attachment; filename=indicator_data.csv'
        return response


class CountryExport(View):

    def get(self, *args, **kwargs):
        country = CountryResource().export()
        response = HttpResponse(country.csv, content_type="csv")
        response['Content-Disposition'] = 'attachment; filename=country.csv'
        return response


def const_table_det_url(url):
    url_data = urlparse(url)
    root = url_data.scheme
    org_host = url_data.netloc
    path = url_data.path
    components = re.split('/', path)

    s = []
    for c in components:
        s.append(c)

    new_url = str(root)+'://'+str(org_host)+'/silo_detail/'+str(s[3])+'/'

    return new_url


def add_indicator(request):
    data = request.POST
    program = Program.objects.get(id=data.get('workflowlevel1'))

    indicator = Indicator.objects.create(name=data.get('indicator_name'))
    indicator.program.add(program)

    if indicator.id:
        return HttpResponse({'success': False})

    return HttpResponse({'success': True})


# Objectives

def objectives_list(request):
    if request.method == 'POST':
        data = request.POST

        objective = Objective(
            name=data.get('objective_name'),
            description=data.get('description'),
            program_id=int(data.get('program')),
            parent_id=int(
                data.get('parent_objective')) if data.get('parent_objective') else None
        )

        objective.save()

        if (data.get('saveObjectiveAndNew')):
            return HttpResponseRedirect('/indicators/objectives?quick-action=true')

        return HttpResponseRedirect('/indicators/objectives')

    get_all_objectives = Objective.objects.filter(
        program__organization=request.user.activity_user.organization
    )
    get_programs = Program.objects.filter(
        organization=request.user.activity_user.organization)

    context = {
        'get_all_objectives': get_all_objectives,
        'active': ['indicators'],
        'get_programs': get_programs
    }

    return render(request, 'components/objectives.html', context)


def objectives_tree(request):
    get_all_objectives = Objective.objects.filter(
        program__organization=request.user.activity_user.organization)

    objectives_as_json = {
        '0': {
            'name': 'Strategic Objectives',
            'children': []
        }
    }

    get_programs = Program.objects.all().filter(
        organization=request.user.activity_user.organization).distinct()

    for objective in get_all_objectives:
        data = {'name': objective.name, 'program': objective.program.name, 'children': []}

        if str(objective.id) not in objectives_as_json:
            objectives_as_json[str(objective.id)] = data

        if objective.parent is None:
            objectives_as_json['0']['children'].append(objective.id)
        else:
            if str(objective.parent.id) not in objectives_as_json:
                objectives_as_json[str(objective.parent.id)] = {
                    'name': objective.parent.name,
                    'program': objective.parent.program.name,
                    'children': [objective.id]
                }
            else:
                objectives_as_json[str(objective.parent.id)]['children'].append(objective.id)

    context = {'get_all_objectives': get_all_objectives,
               'objectives_as_json': objectives_as_json,
               'get_programs': get_programs}

    return render(request, 'components/objectives-tree.html', context)


class StrategicObjectiveUpdateView(UpdateView):
    model = StrategicObjective
    template_name_suffix = '_update_form'
    success_url = '/workflow/objectives'
    form_class = StrategicObjectiveForm

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(StrategicObjectiveUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['current_objective'] = self.get_object()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(StrategicObjectiveUpdateView,
                        self).get_context_data(**kwargs)
        context['current_objective'] = self.get_object()
        return context


"""
Objectives views Vue.js
"""
class ObjectiveView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Objective.objects.all()
    serializer_class = ObjectiveSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.data['organization'] = request.user.activity_user.organization.id
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        organization = self.request.user.activity_user.organization.id
        return Objective.objects.filter(organization=organization)


# Vue.js Views
"""
DataCollectionFrequency views
"""


class DataCollectionFrequencyView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = DataCollectionFrequency.objects.all()
    serializer_class = DataCollectionFrequencySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.data['organization'] = request.user.activity_user.organization.id
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        organization = self.request.user.activity_user.organization.id
        return DataCollectionFrequency.objects.filter(organization=organization)

"""
Level views
"""

class LevelView(generics.ListCreateAPIView,
                        generics.RetrieveUpdateDestroyAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.data['organization'] = request.user.activity_user.organization.id
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        organization = self.request.user.activity_user.organization.id
        return Level.objects.filter(organization=organization)


"""
Indicator Type views
"""


class IndicatorTypeView(generics.ListCreateAPIView,
                        generics.RetrieveUpdateDestroyAPIView):
    queryset = IndicatorType.objects.all()
    serializer_class = IndicatorTypeSerializer
    permission_classes = [IsAuthenticated, IsReadOnly]

    def post(self, request, *args, **kwargs):
        request.data['organization'] = request.user.activity_user.organization.id
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        organization = self.request.user.activity_user.organization.id
        return IndicatorType.objects.filter(organization=organization)


"""
Periodic Target View
"""


class PeriodicTargetCreateView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = PeriodicTarget.objects.all()
    serializer_class = PeriodicTargetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization = self.request.user.activity_user.organization
        return PeriodicTarget.objects.filter(indicator__program__organization=organization)

    def post(self, request, *args, **kwargs):
        all_data = request.data['data']
        indicator_data = {
            'lop_target': all_data['indicator_LOP'],
            'baseline': all_data['indicator_baseline'],
            'rationale_for_target': all_data['rationale'],
        }

        periodic_data = all_data['periodic_targets']

        serialized = self.serializer_class(data=periodic_data, many=True)

        if serialized.is_valid():
            serialized.save(indicator_id=all_data['indicator_id'])
            indicator = Indicator.objects.filter(id=all_data['indicator_id'])
            indicator.update(**indicator_data)
            return Response({'data': PeriodicTargetSerializer(self.get_queryset(), many=True).data}, status=status.HTTP_201_CREATED)
        
        print(serialized.errors)
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        targets = self.get_queryset()
        data = request.data['data']
        periodic_data = data['periodic_targets']
        updated_data = []
        indicator_data = {
            'lop_target': data['indicator_LOP'],
            'baseline': data['indicator_baseline'],
            'rationale_for_target': data['rationale'],
        }

        for periodic_target in periodic_data:
            if periodic_target["target_value"] != periodic_target["target"]:
                updated_data.append(periodic_target)

        for target in targets:
            for data in updated_data:
                if data['pk'] == target.id:
                    serializer = self.serializer_class(instance=target, data=data,)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

        indicator = Indicator.objects.filter(id=data['indicator_id'])
        indicator.update(**indicator_data)

        return Response({'data': PeriodicTargetSerializer(self.get_queryset(), many=True).data},
                        status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        id = request.data['id']
        queryset = PeriodicTarget.objects.filter(indicator__id=id)
        queryset.delete()
        indicator_data = {
            'lop_target': None,
            'baseline': None,
            'rationale_for_target': None,
        }
        indicator = Indicator.objects.filter(id=id)
        indicator.update(**indicator_data)
        return Response({'data': PeriodicTargetSerializer(self.get_queryset(), many=True).data},
                        status=status.HTTP_200_OK)


class IndicatorDataView(GView):
    """
    View to fetch indicator data
    """
    def get(self, request):
        try:
            organization = Organization.objects.get(id=request.user.activity_user.organization.id)
            indicators = Indicator.objects.filter(program__organization=organization)

            return JsonResponse({
                    'level_1_label': organization.level_1_label,
                    'indicators':  IndicatorSerializer(indicators, many=True).data
                })
        except Exception as e:
            return JsonResponse(dict(error=str(e)))
