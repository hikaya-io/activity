from rest_framework import serializers
from formlibrary.models import Individual, TrainingAttendance, Distribution
from workflow.models import SiteProfile, Program


class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingAttendance
        fields = ['id', 'training_name', 'training_duration']


class DistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribution
        fields = ['id', 'distribution_name']


class SiteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteProfile
        fields = ['id', 'name']


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ['id', 'name']


class IndividualSerializer(serializers.ModelSerializer):
    training = TrainingSerializer(many=True, read_only=True)
    distribution = DistributionSerializer(many=True, read_only=True)
    site = SiteProfileSerializer(read_only=True)
    program = ProgramSerializer

    class Meta:
        model = Individual
        fields = ['id', 'first_name', 'age', 'gender', 'training', 'distribution', 'site', 'program']
