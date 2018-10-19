from django.contrib import admin
from .models import *
from workflow.models import Sector, Country, Program
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin


class IndicatorResource(resources.ModelResource):

    indicator_type = ManyToManyWidget(IndicatorType, separator=" | ", field="indicator_type")
    objective = ManyToManyWidget(Objective, separator=" | ", field="objective"),
    strategic_objective = ManyToManyWidget(StrategicObjective, separator=" | ", field="strategic_objective")
    level = ManyToManyWidget(Level, separator=" | ", field="level")
    reporting_frequency = fields.Field(column_name='reporting_frequency', attribute='reporting_frequency', widget=ForeignKeyWidget(ReportingFrequency, 'frequency'))
    sector = fields.Field(column_name='sector', attribute='sector', widget=ForeignKeyWidget(Sector, 'sector'))
    program = ManyToManyWidget(Program, separator=" | ", field="name")

    class Meta:
        model = Indicator
        fields = ('id','indicator_type','level','objective','strategic_objective','name','number',\
                  'source','definition', 'justification', 'unit_of_measure', 'baseline','lop_target', 'rationale_for_target', 'means_of_verification','data_collection_method', 'data_collection_frequency', 'data_points', 'responsible_person',\
                  'method_of_analysis','information_use','reporting_frequency', 'quality_assurance', 'data_issues', 'indicator_changes', 'comments','disaggregation','sector',\
                  'program','key_performance_indicator')
        #import_id_fields = ['id']


class IndicatorAdmin(ImportExportModelAdmin,SimpleHistoryAdmin):
    resource_class = IndicatorResource
    list_display = ('indicator_types','name','sector','key_performance_indicator')
    search_fields = ('name','number','program__name')
    list_filter = ('program','key_performance_indicator','sector')
    display = 'Indicators'
    filter_horizontal = ('program','objectives','strategic_objectives','disaggregation','program')
    pass


class TolaTableResource(resources.ModelResource):

    class Meta:
        model = TolaTable
        fields = ('id','name','table_id','owner','remote_owner','url')
        #import_id_fields = ['id']


class TolaTableAdmin(ImportExportModelAdmin):
    list_display = ('name','owner','url','create_date','edit_date')
    search_fields = ('country__country','name')
    list_filter = ('country__country',)
    display = 'Tola Table'
    pass

class CollectedDataResource(resources.ModelResource):

    class Meta:
        model = CollectedData
        #import_id_fields = ['id']


class CollectedDataAdmin(ImportExportModelAdmin,SimpleHistoryAdmin):
    resource_class = CollectedDataResource
    list_display = ('indicator','program','agreement')
    search_fields = ('indicator','agreement','program','owner__username')
    list_filter = ('indicator__program__country__country','program','approved_by')
    display = 'Collected Data on Indicators'
    pass


class ReportingFrequencyAdmin(admin.ModelAdmin):
    list_display = ('frequency','description','create_date','edit_date')
    display = 'Reporting Frequency'


admin.site.register(IndicatorType)
admin.site.register(Indicator,IndicatorAdmin)
admin.site.register(ReportingFrequency)
admin.site.register(DisaggregationType, DisaggregationTypeAdmin)
admin.site.register(DisaggregationLabel, DisaggregationLabelAdmin)
admin.site.register(CollectedData, CollectedDataAdmin)
admin.site.register(Objective,ObjectiveAdmin)
admin.site.register(StrategicObjective, StrategicObjectiveAdmin)
admin.site.register(Level)
admin.site.register(ExternalService, ExternalServiceAdmin)
admin.site.register(ExternalServiceRecord, ExternalServiceRecordAdmin)
admin.site.register(TolaTable, TolaTableAdmin)
admin.site.register(DataCollectionFrequency)
admin.site.register(PeriodicTarget, PeriodicTargetAdmin)
