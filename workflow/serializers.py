from rest_framework import serializers

from workflow.models import (
    Office, StakeholderType, Organization, Program,
    )

class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = '__all__'


class StakeholderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StakeholderType
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'
