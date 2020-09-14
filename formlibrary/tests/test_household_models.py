from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from formlibrary.models import Household
from workflow.models import Program


class HouseholdTestCase(TestCase):

    fixtures = [
        'fixtures/tests/users.json',
        'fixtures/tests/activity-users.json',
        'fixtures/tests/programs.json',
        'fixtures/tests/organization.json',
    ]

    def setUp(self):
        self.user = User.objects.first()
        self.program = Program.objects.first()
        self.household = Household.objects.create(
            name="John Doe",
            program_id=self.program.id,
            street="TestStreet"
        )

        self.client = APIClient()

    def test_household_create(self):
        """Check for the Household object"""
        household = Household.objects.get(name="John Doe")
        self.assertEqual(Household.objects.filter(
            id=household.id).count(), 1)
        self.assertEqual(household.street, 'TestStreet')

    def test_edit_individual(self):
        household = Household.objects.first()
        household.street = "Street2"
        household.save()

        edited_household = Household.objects.get(pk=household.pk)
        self.assertEqual(edited_household.street, "Street2")

    def test_delete_individual(self):
        household = Household.objects.filter(name="Nate")
        household.delete()
        self.assertEqual(household.count(), 0)
