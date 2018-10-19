import django_tables2 as tables
from indicators.models import Indicator, CollectedData
from django_tables2.utils import A
from django.template.defaultfilters import floatformat

class AchievedColumn(tables.Column):
    def render(self, value):
        return floatformat(value, -2)

class IndicatorDataTable(tables.Table):

    indicator__name = tables.LinkColumn('indicator_data_report', args=[A('indicator__id'), A('indicator__program__id'), 0])
    actuals = AchievedColumn()

    class Meta:
        model = CollectedData
        attrs = {"class": "paleblue"}
        fields = ('indicator__lop_target', 'actuals','indicator__program__name', 'indicator__number', 'indicator__name')
        sequence = ('indicator__lop_target', 'actuals', 'indicator__program__name','indicator__number', 'indicator__name')


class CollectedDataTable(tables.Table):

    agreement = tables.LinkColumn('projectagreement_update', args=[A('agreement_id')])

    class Meta:
        model = CollectedData
        attrs = {"class": "paleblue"}
        fields = ('targeted', 'achieved', 'description', 'logframe_indicator', 'sector', 'community', 'agreement', 'complete')
        sequence = ('targeted', 'achieved', 'description', 'logframe_indicator', 'sector', 'community', 'agreement', 'complete')