from rest_framework import serializers

from workflow.models import Office, StakeholderType, Organization, ProjectStatus


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


class ProjectStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStatus
        fields = '__all__'

