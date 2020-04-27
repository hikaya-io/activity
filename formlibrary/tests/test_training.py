from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from workflow.models import Program
from formlibrary.models import Individual, Household, Training

class TestTraining(TestCase):
    """
    Test the Training model
    """

    fixtures = ['fixtures/organization.json']

    # Spec: https://github.com/hikaya-io/activity/issues/420
    # ? How does Service Type interact with other models
    def setUp(self):
        self.training = Training.objects.create(
            name="Training 1",
            description="Description training 1",
            program=None,
            office=None,
            site=None,
            implementer=None,
            cases=None,
            # cases=[self.individual, self.household],
            start_date="04/01/2020",
            end_date="04/15/2020",
            form_verified_by="Bruce",
            duration=30,
            # trainers=None
            trainer=None
        )
        # self.training.cases.add(self.individual, self.household)

    def test_duration(self):
        """
        Test duration field is calculated is coherent with start/end dates
        Still under discussion
        """
        print(self.training)

    def test_total_number_of_participants(self):
        """
        Test the total number of participants in a Training is calculated
        properly from related Individuals/Households
        Still WIP
        """
        print(self.training)
        # print(self.training.name)
        # self.assertIs(self.training.cases, None)

    ################################
    # Start/End dates testing
    ################################
    def test_dates(self):
        self.assertIsInstance(self.training.start_date, models.DateField)
        self.assertIsInstance(self.training.end_date, models.DateField)

    def test_start_end_dates(self):
        "Test validation of start/end dates"
        # ! Hint: https://docs.djangoproject.com/en/3.0/ref/models/instances/#validating-objects
        with self.assertRaises(ValidationError):
            Training.objects.create(
                name="Training 2",
                description="End date < Start date",
                start_date="04/15/2020",
                end_date="01/01/2019",
                duration=0
            )
