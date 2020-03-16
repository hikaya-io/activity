from rest_framework import serializers

from indicators.models import (
    Indicator, IndicatorType, PeriodicTarget, CollectedData, 
    DataCollectionFrequency, Objective, Level
    )

class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        fields = '__all__'


class IndicatorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicatorType
        fields = '__all__'


class CollectedDataSerializer(serializers.ModelSerializer):
    date_collected = serializers.DateTimeField(format='%Y-%m-%d')

    class Meta:
        model = CollectedData
        fields = '__all__'


class PeriodicTargetSerializer(serializers.ModelSerializer):
    collecteddata_set = CollectedDataSerializer(many=True, read_only=True)
    indicator = serializers.SerializerMethodField()

    class Meta:
        model = PeriodicTarget
        fields = ['id', 'period', 'start_date', 'end_date', 'target', 'collecteddata_set', 'indicator']

    def get_indicator(self, obj):
        return {"indicator_id": obj.indicator.id,
                "baseline": obj.indicator.baseline,
                "indicator_lop": obj.indicator.lop_target,
                "rationale": obj.indicator.rationale_for_target}


class DataCollectionFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = DataCollectionFrequency
        fields = '__all__'

class ObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Objective
        fields = '__all__'

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'
