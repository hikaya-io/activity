from rest_framework import serializers

from formlibrary.models import Beneficiary, TrainingAttendance


class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingAttendance
        fields = ['training_duration']


class BeneficiarySerializer(serializers.ModelSerializer):
    training = TrainingSerializer(many=True, read_only=True)

    class Meta:
        model = Beneficiary
        fields = ['id', 'beneficiary_name', 'age', 'training']
