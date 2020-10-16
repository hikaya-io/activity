from rest_framework import serializers
from formlibrary.models import Individual, Training, Distribution, Household
from workflow.serializers import SiteProfileSerializer, ProgramSerializer
from feed.serializers import ActivityUserSerializer


class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = ['id', 'name']


class DistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribution
        fields = ['id', 'name']


class IndividualSerializer(serializers.ModelSerializer):
    training = TrainingSerializer(many=True, read_only=True)
    distribution = DistributionSerializer(many=True, read_only=True)
    site = SiteProfileSerializer(read_only=True)
    program = ProgramSerializer

    class Meta:
        model = Individual
        fields = ['id', 'first_name', 'last_name', 'id_number', 'primary_phone',
                  'date_of_birth', 'sex', 'age',
                  'training', 'distribution', 'site', 'program', 'create_date']

        def get_age(self, obj):
            return obj.individual.age()


class HouseholdSerializer(serializers.ModelSerializer):

    class Meta:
        model = Household
        exclude = ['postal_code']


class HouseholdListDataSerializer(serializers.ModelSerializer):
    program = ProgramSerializer()
    created_by = ActivityUserSerializer()

    class Meta:
        model = Household
        fields = ['id', 'name', 'program', 'created_by', 'create_date']


class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields= '__all__'
    # program = ProgramSerializer()
    # program = serializers.IntegerField(required=False)

    # class Meta:
    #     model = Training
    #     fields = ['id', 'name', 'program', 'duration', 'start_date', 'end_date']


class TrainingListSerializer(serializers.ModelSerializer):
    program = ProgramSerializer()
    program = serializers.IntegerField(required=False)

    class Meta:
        model = Training
        fields = ['id', 'name', 'program', 'duration', 'start_date', 'end_date']
