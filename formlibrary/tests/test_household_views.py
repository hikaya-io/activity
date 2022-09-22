from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from formlibrary.views import (
    HouseholdlList, HouseholdDataView
)
from workflow.models import ActivityUser, Organization


class HouseholdViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testUser', password='123456')
        organization = Organization.objects.create(
            name="testOrganization",
            description="description",
        )
        self.activity_user = ActivityUser.objects.create(
                    user=self.user)
        self.activity_user.organization = organization

    def test_household_list(self):
        factory = RequestFactory()
        request = factory.get('household_list')
        request.user = self.user
        request.activity_user = self.activity_user
        response = HouseholdlList.as_view()(request)
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn(request.user.username.encode(), response.content)

    def test_household_list_data(self):
        factory = RequestFactory()
        url = reverse('household_list_data')
        request = factory.get(url)
        request.user = self.user
        request.activity_user = self.activity_user
        response = HouseholdDataView.as_view()(request)
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn(request.activity_user.organization.household_label.encode(), response.content)
