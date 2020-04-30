from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from workflow.models import Program, Office, ActivityUser
from formlibrary.models import Training, Service


class TestTraining(TestCase):
    """
    Test the Training model
    """

    fixtures = [
        'fixtures/tests/organization.json',
        'fixtures/tests/trainings.json',
        'fixtures/tests/programs.json',
        'fixtures/tests/offices.json',
        'fixtures/tests/users.json',
        'fixtures/tests/activity-users.json',
    ]

    # Spec: https://github.com/hikaya-io/activity/issues/420
    # ? How does Service Type interact with other models
    def setUp(self):
        self.activity_user = ActivityUser.objects.first()
        self.program = Program.objects.first()
        self.office = Office.objects.first()
        self.training = Training.objects.create(
            name="Training 1",
            description="Description training 1",
            program=self.program,
            office=self.office,
            start_date="04/01/2020",
            end_date="04/15/2020",
            form_verified_by="Bruce",
            duration=30,
            created_by=self.activity_user,
            modified_by=self.activity_user
        )
        self.program.training_set.add(self.training)

    def test_create_training(self):
        training = Training.objects.create(
            name="New Training",
            description="Newly created training",
            duration=30,
            created_by=self.activity_user,
            modified_by=self.activity_user
        )
        # Test the inheritance
        self.assertIsInstance(training, Service)
        # Check the Training is well saved
        created_training = Training.objects.get(pk=training.pk)
        self.assertEqual(training.name, created_training.name)
        self.assertEqual(training.description, created_training.description)
        self.assertEqual(training.duration, created_training.duration)
        self.assertIsNone(training.program)
        self.assertIsNone(training.office)
        # Assert created date has been set and = modified date
        # self.assertEqual(training.create_date, training.edit_date)

    def test_edit_training(self):
        training = Training.objects.first()
        # created_at = training.create_date
        training.name = "New name for the training"
        training.save()
        self.assertEqual(training.name, "New name for the training")
        # self.assertNotEqual(edit_date, created_at)

    def test_relationships(self):
        """
        Test that the relationships of Training model can be set
        """
        # TODO Use self.training, self.program, self.office...
        print(self)

    def test_reverse_relationships(self):
        """
        Test how the reverse relationships of Training are set
        """
        # TODO Use self.training, self.program, self.office...
        print(self)

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
                duration=0,
                created_by=self.activity_user,
                modified_by=self.activity_user
            )

    def test_tracks_creator_and_modifier(self):
        # Properly testing this requires simulating a logged in user
        self.assertIsInstance(self.training.created_by, ActivityUser)
        self.assertIsInstance(self.training.modified_by, ActivityUser)
