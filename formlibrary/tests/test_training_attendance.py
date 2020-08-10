from django.test import TestCase
from formlibrary.models import Individual, Household
import datetime


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
        household = Household.objects.create(name="MyHouse", primary_phone='40-29104782')
        individual = Individual.objects.create(
            first_name="Nate", last_name="Test", date_of_birth=datetime.date(2000, 10, 10),
            sex="Male", signature=False, description="life", household_id=household)
        individual.save()

    def test_individual_exists(self):
        """Check for the Individual object"""
        get_individual = Individual.objects.get(first_name="Nate")
        self.assertEqual(Individual.objects.filter(
            id=get_individual.id).count(), 1)
        self.assertEqual(get_individual.age, 19)
        self.assertEqual(get_individual.sex, 'Male')
        self.assertIsInstance(get_individual.household_id, Household)
