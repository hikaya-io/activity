from rest_framework import serializers

from formlibrary.models import Individual, TrainingAttendance


class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingAttendance
        fields = ['training_duration']


class IndividualSerializer(serializers.ModelSerializer):
    training = TrainingSerializer(many=True, read_only=True)

    class Meta:
        model = Individual
        fields = ['id', 'beneficiary_name', 'age', 'training']
