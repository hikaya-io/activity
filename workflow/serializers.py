from rest_framework import serializers

from workflow.models import Office, StakeholderType


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = '__all__'


class StakeholderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StakeholderType
        fields = '__all__'

