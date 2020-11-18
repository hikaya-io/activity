from django.test import TestCase
from formlibrary.models import Training, Distribution
from workflow.models import Program, Office, ActivityUser
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from pytz import timezone
from datetime import datetime
from django.urls import reverse


class ServiceTestCase(TestCase):
    fixtures = [
        'fixtures/tests/organization.json',
        'fixtures/tests/programs.json',
        'fixtures/tests/users.json',
        'fixtures/tests/offices.json',
        'fixtures/tests/activity-users.json',
    ]

    def setUp(self):
        self.activity_user = ActivityUser.objects.first()
        self.user = User.objects.first()
        self.program = Program.objects.first()
        self.office = Office.objects.first()
        self.training = Training.objects.create(
            name="Training 1",
            description="Description training 1",
            program=self.program,
            office=self.office,
            start_date=datetime.strptime("2020-10-01 15:34", "%Y-%m-%d %H:%M").replace(tzinfo=timezone('UTC')),
            end_date=datetime.strptime("2020-10-19 15:55", "%Y-%m-%d %H:%M").replace(tzinfo=timezone('UTC')),
            form_verified_by="Bruce",
            duration=30,
            created_by=self.activity_user,
            modified_by=self.activity_user,
        )
        self.distribution = Distribution.objects.create(
            name="Distribution 1",
            program_id='1',
            start_date=datetime.strptime("2020-10-01 15:34", "%Y-%m-%d %H:%M").replace(tzinfo=timezone('UTC')),
            end_date=datetime.strptime("2020-10-19 15:55", "%Y-%m-%d %H:%M").replace(tzinfo=timezone('UTC')),
            quantity=1,
            item_distributed="test"
        )
        self.client = APIClient()

    def test_service_training_edit(self):
        url = reverse("training_update", args=[self.training.id])
        self.client.force_login(self.user, backend=None)

        data = {
            'end_date': datetime.strptime("2020-10-20 15:55", "%Y-%m-%d %H:%M").replace(tzinfo=timezone('UTC')),
            'duration': 10,
        }

        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 200)

    def test_service_delete_training_request(self):
        url = reverse("training", kwargs={'pk': self.training.pk})
        self.client.force_login(self.user, backend=None)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)

    def test_service_get_training_list(self):
        url = reverse("training_data")
        self.client.force_login(self.user, backend=None)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_service_distribution_edit(self):
        url = reverse("distribution_update", args=[self.distribution.id])
        self.client.force_login(self.user, backend=None)

        data = {
            'end_date': datetime.strptime("2020-10-20 15:55", "%Y-%m-%d %H:%M").replace(tzinfo=timezone('UTC')),
            'quantity': 3,
        }

        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 200)

    def test_service_delete_distribution_request(self):
        url = reverse("distribution", kwargs={'pk': self.distribution.pk})
        self.client.force_login(self.user, backend=None)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)

    def test_service_get_distribution_list(self):
        url = reverse("distribution_data")
        self.client.force_login(self.user, backend=None)

        resp = self.client.get(url)
        print("*********")
        print(resp)
        self.assertEqual(resp.status_code, 200)
