from rest_framework import serializers

from indicators.models import (
    Indicator, IndicatorType, PeriodicTarget, CollectedData,
    DataCollectionFrequency, Objective, Level, DisaggregationLabel,
    DisaggregationType, DisaggregationValue
    )
from workflow.models import Documentation
from workflow.serializers import ProgramSerializer


class DisaggregationLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisaggregationLabel
        fields = '__all__'


class DisaggregationTypeSerializer(serializers.ModelSerializer):
    disaggregation_label = DisaggregationLabelSerializer(many=True)

    class Meta:
        model = DisaggregationType
        fields = ['id', 'disaggregation_type', 'standard', 'disaggregation_label']


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'


class IndicatorSerializer(serializers.ModelSerializer):
    disaggregation = DisaggregationTypeSerializer(read_only=True, many=True)
    program = ProgramSerializer(read_only=True, many=True)
    level = LevelSerializer(read_only=True, many=True)

    class Meta:
        model = Indicator
        fields = ['id', 'name', 'lop_target', 'baseline', 'rationale_for_target', 'number',
                  'unit_of_measure', 'disaggregation', 'program', 'level']


class DisaggregationValueSerializer(serializers.ModelSerializer):
    disaggregation_label = DisaggregationLabelSerializer()

    class Meta:
        model = DisaggregationValue
        fields = ['id', 'value', 'disaggregation_label']


class IndicatorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicatorType
        fields = '__all__'


class CollectedDataSerializer(serializers.ModelSerializer):
    date_collected = serializers.DateTimeField(format='%Y-%m-%d')
    disaggregation_value = DisaggregationValueSerializer(many=True, read_only=True)

    class Meta:
        model = CollectedData
        fields = ['id', 'periodic_target', 'targeted',
                  'achieved', 'description', 'indicator',
                  'date_collected', 'evidence', 'disaggregation_value']


class PeriodicTargetSerializer(serializers.ModelSerializer):
    collecteddata_set = CollectedDataSerializer(many=True, read_only=True)
    indicator = serializers.SerializerMethodField()

    class Meta:
        model = PeriodicTarget
        fields = ['id', 'period', 'start_date', 'end_date', 'target', 'collecteddata_set', 'indicator']

    def get_indicator(self, obj):
        return {"id": obj.indicator.id,
                "baseline": obj.indicator.baseline,
                "lop_target": obj.indicator.lop_target,
                "rationale_for_target": obj.indicator.rationale_for_target,
                }


class DataCollectionFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = DataCollectionFrequency
        fields = '__all__'


class ObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Objective
        fields = '__all__'


class DocumentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documentation
        fields = '__all__'
