from rest_framework import serializers

from indicators.models import Indicator, PeriodicTarget, CollectedData


class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
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
        fields = ['period', 'start_date', 'end_date', 'target', 'collecteddata_set']
