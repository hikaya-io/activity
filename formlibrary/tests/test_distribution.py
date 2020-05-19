from datetime import date
from django.core.exceptions import ValidationError
from django.test import TestCase
from workflow.models import ActivityUser
from formlibrary.models import Distribution, Service


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
            start_date=date(2020, 10, 19),
            end_date=date(2020, 11, 19),
            created_by=self.activity_user,
            modified_by=self.activity_user,
            quantity=100,
        )

    ###############################################
    # CRUD                                        #
    ###############################################
    def test_create_distribution(self):
        distribution = Distribution.objects.create(
            name="New Distribution",
            description="Newly created distribution",
            start_date=date(2020, 10, 19),
            end_date=date(2020, 11, 19),
            created_by=self.activity_user,
            modified_by=self.activity_user,
            quantity=100,
        )
        # Test the inheritance
        self.assertIsInstance(distribution, Service)
        # Check the Training is well saved
        created_distribution = Distribution.objects.get(pk=distribution.pk)
        self.assertEqual(distribution.name, created_distribution.name)
        self.assertEqual(distribution.description, created_distribution.description)
        self.assertEqual(distribution.quantity, created_distribution.quantity)
        self.assertIsNone(distribution.program)
        self.assertIsNone(distribution.office)

    def test_edit_distribution(self):
        distribution = Distribution.objects.first()
        distribution.name = "New Edited Name for Distribution"
        distribution.save()
        updated_distribution = Distribution.objects.get(pk=distribution.pk)
        self.assertEqual(updated_distribution.name, "New Edited Name for Distribution")

    def test_delete_distribution(self):
        # distribution = Distribution.objects.first()
        # distribution.delete()
        print(1)

    ###############################################
    # Dates fields                                #
    ###############################################
    def test_start_end_dates_validation(self):
        "Test validation of start/end dates"
        # ! Hint: https://docs.djangoproject.com/en/3.0/ref/models/instances/#validating-objects
        with self.assertRaises(ValidationError):
            Distribution.objects.create(
                name="Distribution 1",
                description="End date < Start date",
                start_date=date(2020, 10, 19),
                end_date=date(2017, 11, 19),
                created_by=self.activity_user,
                modified_by=self.activity_user,
                quantity=100,
            )

    def test_dates(self):
        self.assertIsInstance(self.distribution.start_date, date)
        self.assertIsInstance(self.distribution.end_date, date)
        self.assertIsInstance(self.distribution.create_date, date)
        self.assertIsInstance(self.distribution.modified_date, date)

    ###############################################
    # Relationships                               #
    ###############################################
    def test_training_cases_relationship(self):
        print(self.distribution)
        print(self.distribution.name)
        self.assertEqual(self.distribution.name, "Distribution 1")

    ###############################################
    # Calculated fields                           #
    ###############################################

    ###############################################
    # Other                                       #
    ###############################################
    def test_tracks_creator_and_modifier(self):
        # Properly testing this requires simulating a logged in user
        self.assertIsInstance(self.distribution.created_by, ActivityUser)
        self.assertIsInstance(self.distribution.modified_by, ActivityUser)
