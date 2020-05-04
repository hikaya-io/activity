from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from workflow.models import ActivityUser
from formlibrary.models import Distribution
from datetime import date

class TestDistribution(TestCase):
    """
    Test the Distribution model
    """

    fixtures = [
        'fixtures/tests/users.json',
        'fixtures/tests/activity-users.json',
        'fixtures/tests/organization.json',
    ]

    # Spec: https://github.com/hikaya-io/activity/issues/420
    # ? How does Service Type interact with other models
    def setUp(self):
        self.activity_user = ActivityUser.objects.first()
        self.distribution = Distribution.objects.create(
            name="Distribution 1",
            description="First distribution",
            created_by=self.activity_user,
            modified_by=self.activity_user
            start_date=date(2020, 10, 1),
            end_date=date(2020, 10, 19),
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
        self.assertIsInstance(self.distribution.start_date, date)
        self.assertIsInstance(self.distribution.end_date, date)

    def test_start_end_dates(self):
        "Test validation of start/end dates"
        # ! Hint: https://docs.djangoproject.com/en/3.0/ref/models/instances/#validating-objects
        with self.assertRaises(ValidationError):
            Distribution.objects.create(
                name="Distribution 2",
                description="End date < Start date",
                created_by=self.activity_user,
                modified_by=self.activity_user
                start_date=date(2020, 10, 19),
                end_date=date(2020, 10, 1),
            )

    def test_tracks_creator_and_modifier(self):
        # Properly testing this requires simulating a logged in user
        self.assertIsInstance(self.distribution.created_by, ActivityUser)
        self.assertIsInstance(self.distribution.modified_by, ActivityUser)