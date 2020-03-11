from rest_framework import serializers

from indicators.models import (
    Indicator, IndicatorType, PeriodicTarget, CollectedData, 
    DataCollectionFrequency, Objective,
    )
from workflow.models import  (Program,)


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

    class Meta:
        model = PeriodicTarget
        fields = ['id', 'period', 'start_date', 'end_date', 'target', 'collecteddata_set']


class DataCollectionFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = DataCollectionFrequency
        fields = '__all__'

class ObjectiveSerializer(serializers.ModelSerializer):
    program_list = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Objective
        fields = '__all__'

    def get_program_list(self, obj):
        return Program.objects.values('id', 'name')