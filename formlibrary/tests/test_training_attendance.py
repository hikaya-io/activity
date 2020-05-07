#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.test import TestCase
from workflow.models import Program
from formlibrary.models import TrainingAttendance, Individual, Training
from datetime import date, datetime
from pytz import timezone


class TrainingAttendanceTestCase(TestCase):

    fixtures = [
        'fixtures/tests/programs.json',
    ]

    def setUp(self):
        program = Program.objects.first()
        # stakeholder_obj = Stakeholder.objects.create(name="test_stakeholder")
        new_training = TrainingAttendance.objects.create(
            training_name="testtraining",
            program=program,
            implementer="test stakeholder",
            reporting_period="34",
            total_participants="34",
            location="34",
            community="34",
            training_duration="34",
            start_date=datetime.strptime("2020-10-01 15:34", "%Y-%m-%d %H:%M").replace(tzinfo=timezone('UTC')),
            end_date=datetime.strptime("2020-10-19 15:55", "%Y-%m-%d %H:%M").replace(tzinfo=timezone('UTC')),
            trainer_name="34",
            trainer_contact_num="34",
            form_filled_by="34",
            form_filled_by_contact_num="34",
            total_male=34,
            total_female=34,
            total_age_0_14_male=34,
            total_age_0_14_female=34,
            total_age_15_24_male=34,
            total_age_15_24_female=34,
            total_age_25_59_male=34
        )
        new_training.save()

    def test_training_exists(self):
        """Check for Training object"""
        get_training = TrainingAttendance.objects.get(
            training_name="testtraining")
        self.assertEqual(TrainingAttendance.objects.filter(
            id=get_training.id).count(), 1)


class IndividualTestCase(TestCase):

    fixtures = [
        # 'fixtures/tests/organization.json',
        'fixtures/tests/trainings.json',
        # 'fixtures/tests/programs.json',
        # 'fixtures/tests/offices.json',
        'fixtures/tests/users.json',
        'fixtures/tests/activity-users.json',
    ]

    def setUp(self):
        training = Training.objects.first()
        individual = Individual.objects.create(
            first_name="Joe Test", father_name="Mr Test", age="42",
            gender="male", signature=False, remarks="life")
        individual.training.add(training)
        individual.save()

    def test_individual_exists(self):
        """Check for the Individual object"""
        get_individual = Individual.objects.get(first_name="Joe Test")
        self.assertEqual(Individual.objects.filter(
            id=get_individual.id).count(), 1)
