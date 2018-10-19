from django.conf.urls import include, url

from .views import CollectedDataList, CollectedDataCreate, CollectedDataUpdate, \
    CollectedDataDelete, IndicatorCreate, IndicatorDelete, IndicatorUpdate,\
    IndicatorList, IndicatorExport, IndicatorReportData,CollectedDataReportData,\
    IndicatorReport, IndicatorDataExport, TVAReport, DisaggregationReport, \
    PeriodicTargetDeleteView, indicator_create, collecteddata_import, indicator_report, \
    programIndicatorReport, indicator_data_report, service_json, collected_data_json,\
    program_indicators_json, TVAPrint, DisaggregationPrint, PeriodicTargetView


urlpatterns = [

    # INDICATOR PLANING TOOL
    # Home
    url(r'^home/(?P<program>\w+)/(?P<indicator>\w+)/(?P<type>\w+)/$', IndicatorList.as_view(), name='indicator_list'),

    # Indicator Form
    url(r'^indicator_list/(?P<pk>\w+)/$', IndicatorList.as_view(), name='indicator_list'),
    url(r'^indicator_create/(?P<id>\w+)/$', indicator_create, name='indicator_create'),
    url(r'^indicator_add/(?P<id>\w+)/$', IndicatorCreate.as_view(), name='indicator_add'),
    url(r'^indicator_update/(?P<pk>\w+)/$', IndicatorUpdate.as_view(), name='indicator_update'),
    url(r'^indicator_delete/(?P<pk>\w+)/$', IndicatorDelete.as_view(), name='indicator_delete'),

    url(r'^periodic_target_delete/(?P<pk>\w+)/$', PeriodicTargetDeleteView.as_view(), name='pt_delete'),
    url(r'^periodic_target_generate/(?P<indicator>\w+)/$', PeriodicTargetView.as_view(), name='pt_generate'),
    url(r'^periodic_target_deleteall/(?P<indicator>\w+)/(?P<deleteall>\w+)/$', PeriodicTargetView.as_view(), name='pt_deleteall'),

    # Collected Data List
    url(r'^collecteddata/(?P<program>\w+)/(?P<indicator>\w+)/(?P<type>\w+)/$', CollectedDataList.as_view(), name='collecteddata_list'),
    url(r'^collecteddata_add/(?P<program>\w+)/(?P<indicator>\w+)/$', CollectedDataCreate.as_view(), name='collecteddata_add'),
    url(r'^collecteddata_import/$', collecteddata_import, name='collecteddata_import'),
    url(r'^collecteddata_update/(?P<pk>\w+)/$', CollectedDataUpdate.as_view(), name='collecteddata_update'),
    url(r'^collecteddata_delete/(?P<pk>\w+)/$', CollectedDataDelete.as_view(), name='collecteddata_delete'),
    url(r'^collecteddata_export/(?P<program>\w+)/(?P<indicator>\w+)/$', CollectedDataList.as_view(), name='collecteddata_list'),

    # Indicator Report
    url(r'^report/(?P<program>\w+)/(?P<indicator>\w+)/(?P<type>\w+)/$', indicator_report, name='indicator_report'),
    url(r'^tvareport/$', TVAReport.as_view(), name='tvareport'),
    url(r'^tvaprint/(?P<program>\w+)/$', TVAPrint.as_view(), name='tvaprint'),
    url(r'^disrep/(?P<program>\w+)/$', DisaggregationReport.as_view(), name='disrep'),
    url(r'^disrepprint/(?P<program>\w+)/$', DisaggregationPrint.as_view(), name='disrepprint'),
    url(r'^report_table/(?P<program>\w+)/(?P<indicator>\w+)/(?P<type>\w+)/$', IndicatorReport.as_view(), name='indicator_table'),
    url(r'^program_report/(?P<program>\w+)/$', programIndicatorReport, name='programIndicatorReport'),

    # Indicator Data Report
    url(r'^data/(?P<id>\w+)/(?P<program>\w+)/(?P<type>\w+)/$', indicator_data_report, name='indicator_data_report'),
    url(r'^data/(?P<id>\w+)/(?P<program>\w+)/(?P<type>\w+)/map/$', indicator_data_report, name='indicator_data_report'),
    url(r'^data/(?P<id>\w+)/(?P<program>\w+)/(?P<type>\w+)/graph/$', indicator_data_report, name='indicator_data_report'),
    url(r'^data/(?P<id>\w+)/(?P<program>\w+)/(?P<type>\w+)/table/$', indicator_data_report, name='indicator_data_report'),
    url(r'^data/(?P<id>\w+)/(?P<program>\w+)/$', indicator_data_report, name='indicator_data_report'),
    url(r'^data/(?P<id>\w+)/$', indicator_data_report, name='indicator_data_report'),
    url(r'^export/(?P<id>\w+)/(?P<program>\w+)/(?P<indicator_type>\w+)/$', IndicatorExport.as_view(), name='indicator_export'),

    # ajax calls
    url(r'^service/(?P<service>[-\w]+)/service_json/', service_json, name='service_json'),
    url(r'^collected_data_table/(?P<indicator>[-\w]+)/(?P<program>[-\w]+)/', collected_data_json, name='collected_data_json'),
    url(r'^program_indicators/(?P<program>[-\w]+)/(?P<indicator>[-\w]+)/(?P<type>[-\w]+)', program_indicators_json, name='program_indicators_json'),
    url(r'^report_data/(?P<id>\w+)/(?P<program>\w+)/(?P<type>\w+)/$', IndicatorReportData.as_view(),name='indicator_report_data'),
    url(r'^report_data/(?P<id>\w+)/(?P<program>\w+)/(?P<indicator_type>\w+)/export/$', IndicatorExport.as_view(),name='indicator_export'),
    url(r'^collecteddata_report_data/(?P<program>\w+)/(?P<indicator>\w+)/(?P<type>\w+)/$', CollectedDataReportData.as_view(), name='collecteddata_report_data'),
    url(r'^collecteddata_report_data/(?P<program>\w+)/(?P<indicator>\w+)/(?P<type>\w+)/export/$', IndicatorDataExport.as_view(), name='collecteddata_report_data'),


]