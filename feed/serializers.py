import json
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import serializers
from workflow.models import Program, Sector, ProjectType, Office, SiteProfile, Country, ProjectComplete, \
    ProjectAgreement, Stakeholder, Capacity, Evaluate, ProfileType, \
    Province, District, AdminLevelThree, Village, StakeholderType, Contact, Documentation, LoggedUser, Checklist, Organization
from indicators.models import Indicator, ReportingFrequency, TolaUser, IndicatorType, Objective, DisaggregationType, \
    Level, ExternalService, ExternalServiceRecord, StrategicObjective, CollectedData, TolaTable, DisaggregationValue,\
    PeriodicTarget
from django.contrib.auth.models import User
from django.core.serializers.python import Serializer as PythonSerializer


class FlatJsonSerializer(PythonSerializer):
    """
    Take a look at the django implementation as a reference if you need further customization:
    https://github.com/django/django/blob/master/django/core/serializers/json.py
    Usage:
        serializer = FlatJsonSerializer()
        json_data = serializer.serialize(<queryset>, <optional>fields=('field1', 'field2'))
    """
    def get_dump_object(self, obj):
        data = self._current
        if not self.selected_fields or 'id' in self.selected_fields:
            data['id'] = obj.id
        return data

    def end_object(self, obj):
        if not self.first:
            self.stream.write(', ')
        json.dump(self.get_dump_object(obj), self.stream,
                  cls=DjangoJSONEncoder)
        self._current = None

    def start_serialization(self):
        self.stream.write("[")

    def end_serialization(self):
        self.stream.write("]")

    def getvalue(self):
        return super(PythonSerializer, self).getvalue()


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

class PeriodicTargetSerializer(serializers.ModelSerializer):

    class Meta:
        model = PeriodicTarget
        fields = '__all__'


class ProgramSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Program
        fields = '__all__'


class SectorSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Sector
        fields = '__all__'


class ProjectTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ProjectType
        fields = '__all__'


class OfficeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Office
        fields = '__all__'


class SiteProfileSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = SiteProfile
        fields = '__all__'


class CompleteSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ProjectComplete
        fields = '__all__'


class AgreementSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ProjectAgreement
        fields=(
                'id',
                'program',
                'date_of_request',
                'project_name',
                'project_type',
                'project_activity',
                'project_description',
                'site',
                'activity_code',
                'office',
                'sector',
                'project_design',
                'account_code',
                'lin_code',
                'stakeholder',
                'effect_or_impact',
                'expected_start_date',
                'expected_end_date',
                'expected_duration',
                'total_estimated_budget',
                'mc_estimated_budget',
                'local_total_estimated_budget',
                'local_mc_estimated_budget',
                'exchange_rate',
                'exchange_rate_date',
                'estimation_date',
                'estimated_by',
                'estimated_by_date',
                'checked_by',
                'checked_by_date',
                'reviewed_by',
                'reviewed_by_date',
                'finance_reviewed_by',
                'finance_reviewed_by_date',
                'me_reviewed_by',
                'me_reviewed_by_date',
                'capacity',
                'evaluate',
                'approval',
                'approved_by',
                'approved_by_date',
                'approval_submitted_by',
                'approval_remarks',
                'justification_background',
                'risks_assumptions',
                'justification_description_community_selection',
                'description_of_project_activities',
                'description_of_government_involvement',
                'description_of_community_involvement',
                'community_project_description')


class CountrySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'


class IndicatorSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Indicator
        fields = '__all__'

class IndicatorTypeLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicatorType
        fields = ('id', 'indicator_type')


class IndicatorLevelLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ('id', 'name')

class IndicatorLightSerializer(serializers.ModelSerializer):
    sector = serializers.SerializerMethodField()
    indicator_type = IndicatorTypeLightSerializer(many=True, read_only=True)
    level = IndicatorLevelLightSerializer(many=True, read_only=True)
    datacount = serializers.SerializerMethodField()

    def get_datacount(self, obj):
        # Returns the number of collecteddata points by an indicator
        return obj.collecteddata_set.count()

    def get_sector(self, obj):
        if obj.sector is None:
            return ''
        return {"id": obj.sector.id, "name": obj.sector.sector}

    class Meta:
        model = Indicator
        fields = ('name', 'number', 'lop_target', 'indicator_type', 'level', 'sector', 'datacount')

class ProgramIndicatorSerializer(serializers.ModelSerializer):
    indicator_set = IndicatorLightSerializer(many=True, read_only=True)
    indicators_count = serializers.SerializerMethodField()

    def get_indicators_count(self, obj):
        return obj.indicator_set.count()

    class Meta:
        model =  Program
        fields = ('id', 'name', 'indicators_count', 'indicator_set')


class ReportingFrequencySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ReportingFrequency
        fields = '__all__'


class TolaUserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = TolaUser
        fields = '__all__'

class IndicatorTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = IndicatorType
        fields = '__all__'


class ObjectiveSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Objective
        fields = '__all__'


class DisaggregationTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DisaggregationType
        fields = '__all__'


class LevelSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Level
        fields = '__all__'


class StakeholderSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Stakeholder
        fields = '__all__'


class ExternalServiceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ExternalService
        fields = '__all__'


class ExternalServiceRecordSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ExternalServiceRecord
        fields = '__all__'


class StrategicObjectiveSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = StrategicObjective
        fields = '__all__'

class StakeholderTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = StakeholderType
        fields = '__all__'


class CapacitySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Capacity
        fields = '__all__'


class EvaluateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Evaluate
        fields = '__all__'


class ProfileTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ProfileType
        fields = '__all__'


class ProvinceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Province
        fields = '__all__'


class DistrictSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = District
        fields = '__all__'


class AdminLevelThreeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = AdminLevelThree
        fields = '__all__'


class VillageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Village
        fields = '__all__'


class ContactSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Contact
        fields = '__all__'


class DocumentationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Documentation
        fields = '__all__'


class CollectedDataSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CollectedData
        fields = '__all__'


class TolaTableSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = TolaTable
        # HyperlinkedModelSerializer does not include id field by default so manually setting it
        fields = ('id', 'name', 'table_id', 'owner', 'remote_owner', 'country', 'url', 'unique_count', 'create_date', 'edit_date')
        #fields = '__all__'

class DisaggregationValueSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DisaggregationValue

class LoggedUserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = LoggedUser
		fields = ('username', 'country', 'email')

class ChecklistSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Checklist
        fields = '__all__'

class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'