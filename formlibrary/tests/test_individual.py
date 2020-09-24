from django.test import TestCase
from formlibrary.models import Individual, Household
from workflow.models import Program
from django.urls import reverse
import datetime
from rest_framework.test import APIClient
from django.contrib.auth.models import User


class IndividualTestCase(TestCase):

    fixtures = [
        'fixtures/tests/users.json',
        'fixtures/tests/activity-users.json',
        'fixtures/tests/programs.json',
        'fixtures/tests/organization.json',
    ]

    def setUp(self):
        self.user = User.objects.first()

        self.household = Household.objects.create(name="MyHouse", primary_phone='40-29104782')
        self.program = Program.objects.first()
        self.individual = Individual.objects.create(
            first_name="Nate",
            last_name="Test",
            date_of_birth=datetime.date(2000, 10, 10),
            sex="M",
            signature=False,
            description="life",
            household_id=self.household,
            program_id=self.program.id
        )

        self.client = APIClient()

    def test_individual_create(self):
        """Check for the Individual object"""
        get_individual = Individual.objects.get(first_name="Nate")
        self.assertEqual(Individual.objects.filter(
            id=get_individual.id).count(), 1)
        self.assertEqual(get_individual.age, 19)
        self.assertEqual(get_individual.sex, 'M')
        self.assertIsInstance(get_individual.household_id, Household)

    def test_individual_does_not_exists(self):
        get_individual = Individual()
        self.assertEqual(Individual.objects.filter(
            id=get_individual.id).count(), 0)

    def test_edit_individual(self):
        individual = Individual.objects.first()
        individual.sex = "F"
        individual.save()

        updated_individual = Individual.objects.get(pk=individual.pk)
        self.assertEqual(updated_individual.sex, "F")

    def test_delete_individual(self):
        individual = Individual.objects.filter(first_name="Nate")
        individual.delete()
        self.assertEqual(individual.count(), 0)

    def test_create_individual_request(self):
        individual = {
            'first_name': 'test',
            'last_name': 'test_last',
            'date_of_birth': '2000-10-10',
            'sex': 'M',
            'signature': False,
            'description': 'life',
            'program': '1'
        }

        url = reverse("individual", kwargs={'pk': 0})
        self.client.force_login(self.user, backend=None)

        resp = self.client.post(url, data=individual)
        self.assertEqual(resp.status_code, 201)

    def test_edit_individual_request(self):

        url = reverse("individual_update", args=[self.individual.id])
        self.client.force_login(self.user, backend=None)

        data = {
            'last_name': 'test_last',
            'sex': 'F',
        }
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 200)

    def test_delete_individual_request(self):
        url = reverse("individual", kwargs={'pk': self.individual.pk})
        self.client.force_login(self.user, backend=None)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
