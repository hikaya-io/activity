#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.test import TestCase
from formlibrary.models import Individual, Training


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
