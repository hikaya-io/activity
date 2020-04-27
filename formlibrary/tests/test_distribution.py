from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from workflow.models import Program
from formlibrary.models import Individual, Household, Distribution

class TestDistribution(TestCase):
    """
    Test the Distribution model
    """

    fixtures = ['fixtures/organization.json']

    # Spec: https://github.com/hikaya-io/activity/issues/420
    # ? How does Service Type interact with other models
    def setUp(self):
        self.distribution = Distribution.objects.create(
            name="Distribution 1",
            description="First distribution",
            start_date="04/01/2020",
            end_date="04/15/2020",
        )
        # self.training.cases.add(self.individual, self.household)

    def test_training_cases_relationship(self):
        print(self.distribution)
        print(self.distribution.name)
        self.assertEqual(self.distribution.name, "Distribution 1")

    def test_start_end_date(self):
        "Test validation of start/end dates"
        print(self.distribution.start_date)

    ################################
    # Start/End dates testing
    ################################
    def test_dates(self):
        self.assertIsInstance(self.distribution.start_date, models.DateField)
        self.assertIsInstance(self.distribution.end_date, models.DateField)

    def test_start_end_dates(self):
        "Test validation of start/end dates"
        # ! Hint: https://docs.djangoproject.com/en/3.0/ref/models/instances/#validating-objects
        with self.assertRaises(ValidationError):
            Distribution.objects.create(
                name="Distribution 2",
                description="End date < Start date",
                start_date="04/15/2020",
                end_date="01/01/2019"
            )
