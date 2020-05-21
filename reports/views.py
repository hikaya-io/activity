#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.views.generic import View
from workflow.models import ProjectAgreement, Program
from indicators.models import CollectedData, Indicator, PeriodicTarget
from indicators.serializers import IndicatorSerializer, PeriodicTargetSerializer

from django.db.models import Q
from workflow.mixins import AjaxableResponseMixin
from django.http import HttpResponse, JsonResponse

import json
import simplejson
import pendulum
import math

from workflow.export import ProjectAgreementResource
from workflow.export import ProgramResource
from indicators.export import CollectedDataResource
from indicators.export import IndicatorResource

from django.views.generic.list import ListView
from django.shortcuts import render

from .utils import create_periods_list


def make_filter(my_request):
    """
    Build a list of filters for each object
    """
    query_attrs = dict()
    query_attrs['program'] = dict()
    query_attrs['project'] = dict()
    query_attrs['indicator'] = dict()
    query_attrs['collecteddata'] = dict()
    for param, val in my_request.items():
        if param == 'program':
            query_attrs['program']['id__in'] = val.split(',')
            query_attrs['project']['program__id__in'] = val.split(',')
            query_attrs['indicator']['program__id__in'] = val.split(',')
            query_attrs['collecteddata'][
                'indicator__program__id__in'] = val.split(
                ',')
        elif param == 'sector':
            query_attrs['program']['sector__in'] = val.split(',')
            query_attrs['project']['sector__in'] = val.split(',')
            query_attrs['indicator']['sector__in'] = val.split(',')
            query_attrs['collecteddata']['indicator__sector__in'] = val.split(
                ',')
        elif param == 'country':
            query_attrs['program']['country__id__in'] = val.split(',')
            query_attrs['project']['program__country__id__in'] = val.split(',')
            query_attrs['indicator']['program__country__in'] = val.split(',')
            query_attrs['collecteddata']['program__country__in'] = val.split(
                ',')
        elif param == 'indicator__id':
            query_attrs['indicator']['id'] = val
            query_attrs['collecteddata']['indicator__id'] = val
        elif param == 'approval':
            if val == "new":
                query_attrs['project']['approval'] = ""
            else:
                query_attrs['project']['approval'] = val
        elif param == 'collecteddata__isnull':
            if val == "True":
                query_attrs['indicator']['collecteddata__isnull'] = True
            else:
                query_attrs['indicator']['collecteddata__isnull'] = False
        elif param == 'export':
            """
            IGNORE EXPORT PARAM
            """
        else:
            query_attrs['program'][param] = val
            query_attrs['project'][param] = val
            query_attrs['indicator'][param] = val
            query_attrs['collecteddata'][param] = val

    return query_attrs


class IndicatorTrackingHome(ListView):
    '''
        Main home page for indicator tracking table
    '''
    model = Indicator
    template_name = 'reports/indicators/indicator_reports.html'

    def get(self, request, *args, **kwargs):
        organization = request.user.activity_user.organization

        return render(request, self.template_name, {
            'organization': organization,
            'active': ['reports']})


class ReportData(View, AjaxableResponseMixin):
    """
    Main report view
    """

    def get(self, request, *args, **kwargs):
        filter = make_filter(self.request.GET)
        program_filter = filter['program']
        project_filter = filter['project']
        indicator_filter = filter['indicator']

        program = Program.objects.all().filter(**program_filter).values(
            'name', 'funding_status', 'cost_center',
            'country__country', 'sector__sector')

        approval_count = ProjectAgreement.objects.all().filter(
            **project_filter).filter(approval='awaiting approval').count()
        approved_count = ProjectAgreement.objects.all().filter(
            **project_filter).filter(approval='approved').count()
        rejected_count = ProjectAgreement.objects.all().filter(
            **project_filter).filter(approval='rejected').count()
        inprogress_count = ProjectAgreement.objects.all().filter(
            **project_filter).filter(approval='in progress').count()
        nostatus_count = ProjectAgreement.objects.all().filter(
            **project_filter).filter(
            Q(Q(approval=None) | Q(approval=""))).count()

        indicator_count = Indicator.objects.all().filter(
            **indicator_filter).filter(collecteddata__isnull=True).count()
        indicator_data_count = Indicator.objects.all().filter(
            **indicator_filter).filter(collecteddata__isnull=False).count()

        program_serialized = json.dumps(list(program))

        final_dict = {
            'criteria': program_filter, 'program': program_serialized,
            'approval_count': approval_count,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'inprogress_count': inprogress_count,
            'nostatus_count': nostatus_count,
            'indicator_count': indicator_count,
            'data_count': indicator_data_count
        }

        if request.GET.get('export'):
            program_export = Program.objects.all().filter(**program_filter)
            program_dataset = ProgramResource().export(program_export)
            response = HttpResponse(
                program_dataset.csv, content_type='application/ms-excel')
            response[
                'Content-Disposition'] = \
                'attachment; filename=program_data.csv'
            return response

        return JsonResponse(final_dict, safe=False)


class ProjectReportData(View, AjaxableResponseMixin):
    """
    Project based report view
    """

    def get(self, request, *args, **kwargs):
        filter = make_filter(self.request.GET)
        project_filter = filter['project']
        indicator_filter = filter['indicator']

        project = ProjectAgreement.objects.all().filter(
            **project_filter).values(
            'program__name', 'project_name',
            'activity_code', 'project_type__name',
            'sector__sector', 'total_estimated_budget', 'approval')
        approval_count = ProjectAgreement.objects.all().filter(
            **project_filter).filter(
            program__funding_status="Funded",
            approval='awaiting approval').count()
        approved_count = ProjectAgreement.objects.all().filter(
            **project_filter).filter(program__funding_status="Funded",
                                     approval='approved').count()
        rejected_count = ProjectAgreement.objects.all().filter(
            **project_filter).filter(program__funding_status="Funded",
                                     approval='rejected').count()
        inprogress_count = ProjectAgreement.objects.all().filter(
            **project_filter).filter(program__funding_status="Funded",
                                     approval='in progress').count()
        nostatus_count = ProjectAgreement.objects.all().filter(
            **project_filter).filter(
            Q(Q(approval=None) | Q(approval=""))).count()
        indicator_count = Indicator.objects.all().filter(
            **indicator_filter).filter(collecteddata__isnull=True).count()
        indicator_data_count = Indicator.objects.all().filter(
            **indicator_filter).filter(collecteddata__isnull=False).count()

        project_serialized = simplejson.dumps(list(project))

        final_dict = {
            'criteria': project_filter, 'project': project_serialized,
            'approval_count': approval_count,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'inprogress_count': inprogress_count,
            'nostatus_count': nostatus_count,
            'indicator_count': indicator_count,
            'data_count': indicator_data_count,
        }

        if request.GET.get('export'):
            project_export = ProjectAgreement.objects.all().filter(
                **project_filter)
            dataset = ProjectAgreementResource().export(project_export)
            response = HttpResponse(
                dataset.csv, content_type='application/ms-excel')
            response[
                'Content-Disposition'] = \
                'attachment; filename=project_data.csv'
            return response

        return JsonResponse(final_dict, safe=False)


class IndicatorReportData(View, AjaxableResponseMixin):
    """
    Indicator based report view
    """

    def get(self, request, *args, **kwargs):
        filter = make_filter(self.request.GET)
        indicator_filter = filter['indicator']

        indicator = Indicator.objects.all().filter(**indicator_filter).values(
            'id', 'program__name', 'program__id', 'name',
            'indicator_type__indicator_type',
            'sector__sector', 'strategic_objectives', 'level__name',
            'lop_target',
            'collecteddata', 'key_performance_indicator')
        indicator_count = Indicator.objects.all().filter(
            **indicator_filter).filter(collecteddata__isnull=True).count()
        indicator_data_count = Indicator.objects.all().filter(
            **indicator_filter).filter(collecteddata__isnull=False).count()

        indicator_serialized = json.dumps(list(indicator))

        final_dict = {
            'criteria': indicator_filter, 'indicator': indicator_serialized,
            'indicator_count': indicator_count,
            'data_count': indicator_data_count
        }

        if request.GET.get('export'):
            indicator_export = Indicator.objects.all().filter(
                **indicator_filter)
            dataset = IndicatorResource().export(indicator_export)
            response = HttpResponse(
                dataset.csv, content_type='application/ms-excel')
            response[
                'Content-Disposition'] = \
                'attachment; filename=indicator_data.csv'
            return response

        return JsonResponse(final_dict, safe=False)


class CollectedDataReportData(View, AjaxableResponseMixin):
    """
    Indicator based report view
    """

    def get(self, request, *args, **kwargs):
        filter = make_filter(self.request.GET)
        collecteddata_filter = filter['collecteddata']

        collecteddata = CollectedData.objects.all().filter(
            **collecteddata_filter).values(
            'indicator__program__name', 'indicator__name', 'indicator__number',
            'targeted', 'achieved')

        collecteddata_serialized = json.dumps(list(collecteddata))

        final_dict = {
            'criteria': collecteddata_filter,
            'collecteddata': collecteddata_serialized,
        }

        if request.GET.get('export'):
            collecteddata_export = CollectedData.objects.all().filter(
                **collecteddata_filter)
            dataset = CollectedDataResource().export(collecteddata_export)
            response = HttpResponse(
                dataset.csv, content_type='application/ms-excel')
            response[
                'Content-Disposition'] = \
                'attachment; filename=collecteddata_data.csv'
            return response

        return JsonResponse(final_dict, safe=False)


def filter_json(request, service, **kwargs):
    """
    For populating indicators in dropdown
    """
    final_dict = {
        'criteria': kwargs}
    JsonResponse(final_dict, safe=False)


class GenerateReport(View):

    def get(self, request, *args, **kwargs):
        program_id = int(self.kwargs.get('program_id'))
        reporting_id = int(self.kwargs.get('reporting_id'))
        raw_data = []
        reporting_periods = [{"id": 1, "label": "Month"},
                             {"id": 2, "label": "Quarter"},
                             {"id": 3, "label": "Year"}]

        for report in reporting_periods:
            if report['id'] == reporting_id:
                report_period = report['label']

        indicators = Indicator.objects.distinct().filter(program__id=program_id)
        for ind in indicators:
            periodic_targets = PeriodicTarget.objects.filter(indicator=ind.id).prefetch_related('collecteddata_set')\
                                                            .order_by('customsort')
            indicator = IndicatorSerializer(ind).data,
            periodic_data = PeriodicTargetSerializer(periodic_targets, many=True).data
            total_targeted = 0
            total_achieved = 0

            for data in indicator:
                baseline = float(data['baseline'])
                program = data['program'][0]
                start_date = program['start_date']
                end_date = program['end_date']

            start = pendulum.parse(start_date)
            end = pendulum.parse(end_date)

            period = pendulum.period(start, end)

            for data in periodic_data:
                for collecteddata in data['collecteddata_set']:
                    total_achieved += float(collecteddata['achieved'])
                    total_targeted += float(collecteddata['targeted'])

            current = None
            previous = None
            count = 1
            raw_period_data = []

            periods = create_periods_list(report_period, period, end)

            for dt in periods:
                target = 0
                actual = 0
                if dt == start:
                    previous = dt
                else:
                    current = dt
                    period = pendulum.period(previous, current)

                    for data in periodic_data:
                        if pendulum.parse(data['end_date']) in period:
                            for collecteddata in data['collecteddata_set']:
                                target += float(collecteddata['targeted'])
                                actual += float(collecteddata['achieved'])

                    name = str(report_period) + ' ' + str(count)

                    if target == 0 and actual == 0:
                        perct_met = "0%"
                    elif target > baseline:
                        perct_met = math.floor(actual / target * 100)
                        perct_met = str(perct_met) + "%"
                    elif target < baseline:
                        perct_met = math.floor(((target - actual / target) + 1) * 100)
                        perct_met = str(perct_met) + "%"
                    raw_period_data.append(dict(
                        name=name,
                        target=target,
                        actual=actual,
                        perct_met=perct_met
                    ))
                    count += 1

                    previous = dt

            if total_targeted > baseline:
                eop_met = math.floor(total_achieved / total_targeted * 100)
                eop_met = str(eop_met) + "%"
            elif total_targeted < baseline:
                eop_met = math.floor((baseline - total_achieved) / (baseline - total_targeted) * 100)
                eop_met = str(eop_met) + "%"

            raw_data.append(dict(
                indicator=indicator,
                periodic_data=periodic_data,
                total_achieved=total_achieved,
                total_targeted=total_targeted,
                total_perct_met=eop_met,
                raw_data=raw_period_data
            ))

        return JsonResponse({'data': raw_data})
