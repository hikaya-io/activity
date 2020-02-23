#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.urls import path
from .views import (
    IndicatorList, add_indicator, indicator_create, IndicatorCreate,
    IndicatorUpdate, IndicatorDelete, PeriodicTargetDeleteView,
    PeriodicTargetView, CollectedDataReportData, CollectedDataCreate, CollectedDataDelete,
    CollectedDataList, CollectedDataUpdate, CollectedDataAdd, CollectedDataEdit,
    CollectedDataDeleteVue, collecteddata_import, indicator_report,
    TVAReport, TVAPrint, DisaggregationReport, DisaggregationPrint, IndicatorReport,
    program_indicator_report, indicator_data_report, IndicatorExport, service_json,
    collected_data_json, program_indicators_json, IndicatorReportData, IndicatorDataExport,
    ObjectiveList, ObjectiveCreate, objectives_list, objectives_tree, ObjectiveUpdateView, objective_delete, LevelList, LevelCreate,
    LevelUpdate, LevelDelete, DisaggregationTypeDeleteView, DisaggregationLabelDeleteView,
    IndicatorTarget, DataCollectionFrequencyCreate, DataCollectionFrequencyList, DataCollectionFrequencyUpdate,
    DataCollectionFrequencyDelete, IndicatorTypeList, IndicatorTypeCreate, IndicatorTypeUpdate, IndicatorTypeDelete,
)

urlpatterns = [

    # INDICATOR PLANING TOOL
    # Home
    path('home/<int:program>/<int:indicator>/<int:type>/',
         IndicatorList.as_view(), name='indicator_list'),

    path('add-indicator', add_indicator, name='add-indicator'),

    # Indicator Form
    path('indicator_list/<int:pk>/',
         IndicatorList.as_view(), name='indicator_list'),
    path('indicator_create/<int:id>/',
         indicator_create, name='indicator_create'),
    path('indicator_add/<int:id>/',
         IndicatorCreate.as_view(), name='indicator_add'),
    path('indicator_update/<int:pk>/',
         IndicatorUpdate.as_view(), name='indicator_update'),
    path('indicator_delete/<int:pk>/',
         IndicatorDelete.as_view(), name='indicator_delete'),

    path('periodic_target_delete/<int:pk>/',
         PeriodicTargetDeleteView.as_view(), name='pt_delete'),
    path('periodic_target_generate/<int:indicator>/',
         PeriodicTargetView.as_view(), name='pt_generate'),
    path('periodic_target_deleteall/<int:indicator>/<slug:deleteall>/',
         PeriodicTargetView.as_view(), name='pt_deleteall'),

    # Collected Data List
    path('collecteddata/<slug:program>/<int:indicator>/<int:type>/',
         CollectedDataList.as_view(), name='collecteddata_list'),
    path('collecteddata_add/<program>/<indicator>/',
         CollectedDataCreate.as_view(), name='collecteddata_add'),
    path('collecteddata/add',
         CollectedDataAdd.as_view(), name='add-collected-data'),
    path('collecteddata_import/', collecteddata_import,
         name='collecteddata_import'),
    path('collecteddata_update/<int:pk>/',
         CollectedDataUpdate.as_view(), name='collecteddata_update'),
    path('collecteddata_delete/<int:pk>/',
         CollectedDataDelete.as_view(), name='collecteddata_delete'),
    path('collecteddata_export/<program>/<indicator>/',
         CollectedDataList.as_view(), name='collecteddata_list'),
    path('collected_data/edit/<int:id>',
         CollectedDataEdit.as_view(), name='edit-collected-data'),
    path('collected_data/delete/<int:id>',
         CollectedDataDeleteVue.as_view(), name='delete-collected-data'),

    # Indicator Report
    path('report/<program>/<indicator>/<type>/',
         indicator_report, name='indicator_report'),
    path('tvareport/', TVAReport.as_view(), name='tvareport'),
    path('tvaprint/<program>/',
         TVAPrint.as_view(), name='tvaprint'),
    path('disrep/<program>/',
         DisaggregationReport.as_view(), name='disrep'),
    path('disrepprint/<program>/',
         DisaggregationPrint.as_view(), name='disrepprint'),
    path('report_table/<program>/<indicator>/<type>/',
         IndicatorReport.as_view(), name='indicator_table'),
    path('program_report/<program>/',
         program_indicator_report, name='program_indicator_report'),

    # Indicator Data Report
    path('data/<id>/<program>/<type>/',
         indicator_data_report, name='indicator_data_report'),
    path('data/<id>/<program>/<type>/map/',
         indicator_data_report, name='indicator_data_report'),
    path('data/<id>/<program>/<type>/graph/',
         indicator_data_report, name='indicator_data_report'),
    path('data/<id>/<program>/<type>/table/',
         indicator_data_report, name='indicator_data_report'),
    path('data/<id>/<program>/',
         indicator_data_report, name='indicator_data_report'),
    path('data/<id>/', indicator_data_report,
         name='indicator_data_report'),
    path('export/<id>/<program>/<indicator_type>/',
         IndicatorExport.as_view(), name='indicator_export'),

    # ajax calls
    path('service/<service>/service_json/',
         service_json, name='service_json'),
    path('collected_data_table/<indicator>/<program>/',
         collected_data_json, name='collected_data_json'),
    path('program_indicators/program>/<indicator>/<type>/',
         program_indicators_json, name='program_indicators_json'),
    path('report_data/<int:id>/<program>/<type>/',
         IndicatorReportData.as_view(), name='indicator_report_data'),
    path('report_data/<int:id>/<program>/<indicator_type>/export/',
         IndicatorExport.as_view(), name='indicator_export'),
    path('collecteddata_report_data/<program>)/<indicator>/<type>/',
         CollectedDataReportData.as_view(), name='collecteddata_report_data'),
    path('collecteddata_report_data/<program>/<indicator>)/<type>)/export/',
         IndicatorDataExport.as_view(), name='collecteddata_report_data'),
    path('get_target/<int:indicator_id>/', IndicatorTarget.as_view(),
         name='indicator-targets'),

    # objectives
     
#    
#     path(
#         'level/edit/<int:id>',
#         LevelUpdate.as_view(),
#         name='level_edit'
#     ),
#     path(
#          'level/delete/<int:id>',
#          LevelDelete.as_view(),
#          name='level_delete'
#      ),
     path(     
        'objective/list',
        ObjectiveList.as_view(),
        name='objective_list'
     ),
     path(
        'objective/add',
        ObjectiveCreate.as_view(),
        name='objective_add'
     ),
     path('objectives', objectives_list, name='objectives'),
     path('objectives/tree', objectives_tree, name='objectives-tree'),
     path('objectives/edit/<int:pk>/', ObjectiveUpdateView.as_view(),
         name='update_strategic_objective'),
     path('objectives/objective_delete/<int:pk>/', objective_delete,
         name='objective_delete'),
     path('disaggregation_type/delete/<int:pk>/',
         DisaggregationTypeDeleteView.as_view(),
         name='disaggregation_type_delete'),
     path(
        'disaggregation_label/delete/<int:pk>/',
        DisaggregationLabelDeleteView.as_view(),
        name='disaggregation_label_delete'),
     

    # Levels Urls
    path(
        'level/list',
        LevelList.as_view(),
        name='level_list'
    ),
    path(
        'level/add',
        LevelCreate.as_view(),
        name='level_add'
    ),
    path(
        'level/edit/<int:id>',
        LevelUpdate.as_view(),
        name='level_edit'
    ),
    path(
         'level/delete/<int:id>',
         LevelDelete.as_view(),
         name='level_delete'
     ),

    # Data DataCollectionFrequency Urls
    path(
        'data_collection_frequency/add',
        DataCollectionFrequencyCreate.as_view(),
        name='data_collection_frequency_add'
    ),
    path(
        'data_collection_frequency/list',
        DataCollectionFrequencyList.as_view(),
        name='data_collection_frequency_list'
    ),
    path(
        'data_collection_frequency/edit/<int:id>',
        DataCollectionFrequencyUpdate.as_view(),
        name='data_collection_frequency_edit'
    ),
    path(
          'data_collection_frequency/delete/<int:id>',
          DataCollectionFrequencyDelete.as_view(),
          name='data_collection_frequency_delete'
    ),

    # Indicator Types Urls
    path(
          'indicator_type/list',
          IndicatorTypeList.as_view(),
          name='indicator_type_list'
    ),
    path(
          'indicator_type/add',
          IndicatorTypeCreate.as_view(),
          name='indicator_type_add'
    ),
    path(
        'indicator_type/edit/<int:id>',
        IndicatorTypeUpdate.as_view(),
        name='indicator_type_edit'
    ),
    path(
         'indicator_type/delete/<int:id>',
         IndicatorTypeDelete.as_view(),
         name='indicator_type_delete'
     ),
]
