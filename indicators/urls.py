#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.urls import re_path, path
from .views import *

urlpatterns = [

    # INDICATOR PLANING TOOL
    # Home
    re_path(r'^home/(?P<program>\w+)/(?P<indicator>\w+)/(?P<type>\w+)/$',
            IndicatorList.as_view(), name='indicator_list'),

    path('add-indicator', add_indicator, name='add-indicator'),

    # Indicator Form
    re_path(r'^indicator_list/(?P<pk>\w+)/$',
            IndicatorList.as_view(), name='indicator_list'),
    re_path(r'^indicator_create/(?P<id>\w+)/$',
            indicator_create, name='indicator_create'),
    re_path(r'^indicator_add/(?P<id>\w+)/$',
            IndicatorCreate.as_view(), name='indicator_add'),
    re_path(r'^indicator_update/(?P<pk>\w+)/$',
            IndicatorUpdate.as_view(), name='indicator_update'),
    re_path(r'^indicator_delete/(?P<pk>\w+)/$',
            IndicatorDelete.as_view(), name='indicator_delete'),

    re_path(r'^periodic_target_delete/(?P<pk>\w+)/$',
            PeriodicTargetDeleteView.as_view(), name='pt_delete'),
    re_path(r'^periodic_target_generate/(?P<indicator>\w+)/$',
            PeriodicTargetView.as_view(), name='pt_generate'),
    re_path(
        r'^periodic_target_deleteall/(?P<indicator>\w+)/(?P<deleteall>\w+)/$',
        PeriodicTargetView.as_view(), name='pt_deleteall'),

    # Collected Data List
    re_path(
        r'^collecteddata/(?P<program>\w+)/(?P<indicator>\w+)/(?P<type>\w+)/$',
        CollectedDataList.as_view(), name='collecteddata_list'),
    re_path(r'^collecteddata_add/(?P<program>\w+)/(?P<indicator>\w+)/$',
            CollectedDataCreate.as_view(), name='collecteddata_add'),
    re_path(r'^collecteddata_import/$', collecteddata_import,
            name='collecteddata_import'),
    re_path(r'^collecteddata_update/(?P<pk>\w+)/$',
            CollectedDataUpdate.as_view(), name='collecteddata_update'),
    re_path(r'^collecteddata_delete/(?P<pk>\w+)/$',
            CollectedDataDelete.as_view(), name='collecteddata_delete'),
    re_path(r'^collecteddata_export/(?P<program>\w+)/(?P<indicator>\w+)/$',
            CollectedDataList.as_view(), name='collecteddata_list'),

    # Indicator Report
    re_path(r'^report/(?P<program>\w+)/(?P<indicator>\w+)/(?P<type>\w+)/$',
            indicator_report, name='indicator_report'),
    re_path(r'^tvareport/$', TVAReport.as_view(), name='tvareport'),
    re_path(r'^tvaprint/(?P<program>\w+)/$',
            TVAPrint.as_view(), name='tvaprint'),
    re_path(r'^disrep/(?P<program>\w+)/$',
            DisaggregationReport.as_view(), name='disrep'),
    re_path(r'^disrepprint/(?P<program>\w+)/$',
            DisaggregationPrint.as_view(), name='disrepprint'),
    re_path(
        r'^report_table/(?P<program>\w+)/(?P<indicator>\w+)/(?P<type>\w+)/$',
        IndicatorReport.as_view(), name='indicator_table'),
    re_path(r'^program_report/(?P<program>\w+)/$',
            program_indicator_report, name='program_indicator_report'),

    # Indicator Data Report
    re_path(r'^data/(?P<id>\w+)/(?P<program>\w+)/(?P<type>\w+)/$',
            indicator_data_report, name='indicator_data_report'),
    re_path(r'^data/(?P<id>\w+)/(?P<program>\w+)/(?P<type>\w+)/map/$',
            indicator_data_report, name='indicator_data_report'),
    re_path(r'^data/(?P<id>\w+)/(?P<program>\w+)/(?P<type>\w+)/graph/$',
            indicator_data_report, name='indicator_data_report'),
    re_path(r'^data/(?P<id>\w+)/(?P<program>\w+)/(?P<type>\w+)/table/$',
            indicator_data_report, name='indicator_data_report'),
    re_path(r'^data/(?P<id>\w+)/(?P<program>\w+)/$',
            indicator_data_report, name='indicator_data_report'),
    re_path(r'^data/(?P<id>\w+)/$', indicator_data_report,
            name='indicator_data_report'),
    re_path(r'^export/(?P<id>\w+)/(?P<program>\w+)/(?P<indicator_type>\w+)/$',
            IndicatorExport.as_view(), name='indicator_export'),

    # ajax calls
    re_path(r'^service/(?P<service>[-\w]+)/service_json/',
            service_json, name='service_json'),
    re_path(
        r'^collected_data_table/(?P<indicator>[-\w]+)/(?P<program>[-\w]+)/',
        collected_data_json, name='collected_data_json'),
    re_path(
        r'^program_indicators/(?P<program>[-\w]+)/'
        r'(?P<indicator>[-\w]+)/(?P<type>[-\w]+)',
        program_indicators_json, name='program_indicators_json'),
    re_path(r'^report_data/(?P<id>\w+)/(?P<program>\w+)/(?P<type>\w+)/$',
            IndicatorReportData.as_view(), name='indicator_report_data'),
    re_path(
        r'^report_data/(?P<id>\w+)/(?P<program>\w+)/'
        r'(?P<indicator_type>\w+)/export/$',
        IndicatorExport.as_view(), name='indicator_export'),
    re_path(
        r'^collecteddata_report_data/(?P<program>\w+)/'
        r'(?P<indicator>\w+)/(?P<type>\w+)/$',
        CollectedDataReportData.as_view(), name='collecteddata_report_data'),
    re_path(
        r'^collecteddata_report_data/(?P<program>\w+)/'
        r'(?P<indicator>\w+)/(?P<type>\w+)/export/$',
        IndicatorDataExport.as_view(), name='collecteddata_report_data'),

    # objectives
    re_path(r'^objectives/edit/(?P<pk>\w+)/$',
            StrategicObjectiveUpdateView.as_view(),
            name='update_strategic_objective'),
    re_path(r'^objectives/objective_delete/(?P<pk>\w+)/$',
            objective_delete, name='objective_delete')
]
