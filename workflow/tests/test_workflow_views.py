#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from workflow.views import (
 GetLevel1DependantData, FundCodeCreate, FundCodeUpdate, FundCodeDelete, FundCodeList,
 list_workflow_level1, GetCountries, ProfileTypeCreate, ProfileTypeList,
 ProfileTypeDelete, ProfileTypeUpdate
 )
from workflow.models import ActivityUser, Organization


class ProgramViewTestCase(TestCase):

    fixtures = ['fixtures/tests/sectors.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testUser', password='123456')
        organization = Organization.objects.create(
            name="testOrg",
            description="description",
        )
        self.activity_user = ActivityUser.objects.create(
                    user=self.user)
        self.activity_user.organization = organization

    def test_list_workflow_level1(self):
        factory = RequestFactory()
        request = factory.get('level1_list')
        request.user = self.user
        request.activity_user = self.activity_user
        response = list_workflow_level1(request)
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn(request.user.username.encode(), response.content)

    def test_GetLevel1DependantData(self):
        factory = RequestFactory()
        url = reverse('level1_dependant_data')
        request = factory.get(url)
        request.user = self.user
        request.activity_user = self.activity_user
        response = GetLevel1DependantData.as_view()(request)
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn(request.activity_user.organization.level_1_label.encode(), response.content)

    def test_GetLevel1DependantData_with_wrong_method(self):
        factory = RequestFactory()
        url = reverse('level1_dependant_data')
        request = factory.delete(url)
        request.user = self.user
        request.activity_user = self.activity_user
        response = GetLevel1DependantData.as_view()(request)
        self.assertTrue(status.is_client_error(response.status_code))


class FundCodeTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testUser', password='123456')
        organization = Organization.objects.create(
            name="name",
            description="description",
        )
        self.activity_user = ActivityUser.objects.create(
                    user=self.user,
                )
        self.activity_user.organization = organization

    def test_FundCodeCreate(self):
        factory = RequestFactory()
        url = reverse('fund_code_add')
        request_data = {"name": "FundCodeTest"}
        request = factory.post(url, data=request_data, content_type='application/json')
        request.user = self.user
        request.activity_user = self.activity_user
        response = FundCodeCreate.as_view()(request)
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn(request_data.get('name').encode(), response.content)

    def test_FundCodeUpdate(self):
        factory = RequestFactory()
        # first create the record
        ur = reverse('fund_code_add')
        request_data = {"name": "FundCodeTest"}
        req = factory.post(ur, data=request_data, content_type='application/json')
        req.user = self.user
        req.activity_user = self.activity_user
        response = FundCodeCreate.as_view()(req)
        kwargs = {"id": 1}
        url = reverse('fund_code_edit', kwargs=kwargs)
        request_data = {"name": "Second"}
        request = factory.put(url, data=request_data, content_type='application/json')
        request.user = self.user
        request.activity_user = self.activity_user
        response = FundCodeUpdate.as_view()(request, **kwargs)
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn(request_data.get('name').encode(), response.content)

    def test_FundCodeUpdate_with_post(self):
        factory = RequestFactory()
        # first create the record
        ur = reverse('fund_code_add')
        request_data = {"name": "FundCodeTest"}
        req = factory.post(ur, data=request_data, content_type='application/json')
        req.user = self.user
        req.activity_user = self.activity_user
        response = FundCodeCreate.as_view()(req)
        kwargs = {"id": 1}
        url = reverse('fund_code_edit', kwargs=kwargs)
        request_data = {"name": "Second"}
        request = factory.post(url, data=request_data, content_type='application/json')
        request.user = self.user
        request.activity_user = self.activity_user
        response = FundCodeUpdate.as_view()(request, **kwargs)
        self.assertTrue(status.is_client_error(response.status_code))

    def test_FundCodeDelete(self):
        factory = RequestFactory()
        # first create the record
        ur = reverse('fund_code_add')
        request_data = {"name": "Trial"}
        req = factory.post(ur, data=request_data, content_type='application/json')
        req.user = self.user
        req.activity_user = self.activity_user
        response = FundCodeCreate.as_view()(req)
        # Delete the created record
        kwargs = {"id": 1}
        url = reverse('fund_code_delete', kwargs=kwargs)
        request = factory.delete(url, content_type='application/json')
        response = FundCodeDelete.as_view()(request, **kwargs)
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn("success".encode(), response.content)

    def test_FundCodeDelete_with_wrong_method(self):
        factory = RequestFactory()
        # first create the record
        ur = reverse('fund_code_add')
        request_data = {"name": "Trial"}
        req = factory.post(ur, data=request_data, content_type='application/json')
        req.user = self.user
        req.activity_user = self.activity_user
        response = FundCodeCreate.as_view()(req)
        # Delete the created record
        kwargs = {"id": 1}
        url = reverse('fund_code_delete', kwargs=kwargs)
        request = factory.put(url, content_type='application/json')
        response = FundCodeDelete.as_view()(request, **kwargs)
        self.assertTrue(status.is_client_error(response.status_code))

    def test_FundCodeList(self):
        factory = RequestFactory()
        url = reverse('fund_code_list')
        request = factory.get(url)
        request.user = self.user
        request.activity_user = self.activity_user
        response = FundCodeList.as_view()(request)
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn("stakeholders".encode(), response.content)
        self.assertIn("fund_codes".encode(), response.content)


class CountriesTestCase(TestCase):

    fixtures = ["fixtures/countries"]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testUser', password='123456')
        organization = Organization.objects.create(
            name="name",
            description="description",
        )
        self.activity_user = ActivityUser.objects.create(
                    user=self.user)
        self.activity_user.organization = organization

    def test_GetCountries(self):
        factory = RequestFactory()
        url = reverse('get_countries')
        request = factory.get(url)
        request.user = self.user
        request.activity_user = self.activity_user
        response = GetCountries.as_view()(request)
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn("country".encode(), response.content)


class ProfileTypeTestCase(TestCase):

    fixtures = ["fixtures/tests/profiletypes"]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testUser', password='123456')
        organization = Organization.objects.create(
            name="name",
            description="description",
        )
        self.activity_user = ActivityUser.objects.create(
                    user=self.user,
        )
        self.activity_user.organization = organization

    def test_ProfileTypeCreate(self):
        factory = RequestFactory()
        url = reverse('profile_type_add')
        request_data = {"profile": "Trial"}
        request = factory.post(url, data=request_data, content_type='application/json')
        request.user = self.user
        request.activity_user = self.activity_user
        response = ProfileTypeCreate.as_view()(request)
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn(request_data.get('profile').encode(), response.content)

    def test_ProfileTypeList(self):
        factory = RequestFactory()
        url = reverse('profile_type_list')
        request = factory.get(url)
        request.user = self.user
        request.activity_user = self.activity_user
        response = ProfileTypeList.as_view()(request)
        self.assertTrue(status.is_success(response.status_code))

    def test_ProfileTypeUpdate(self):
        factory = RequestFactory()
        # first create the record
        ur = reverse('profile_type_add')
        request_data = {"profile": "Trial"}
        req = factory.post(ur, data=request_data, content_type='application/json')
        req.user = self.user
        req.activity_user = self.activity_user
        response = ProfileTypeCreate.as_view()(req)
        kwargs = {"id": 1}
        url = reverse('profile_type_edit', kwargs=kwargs)
        request_data = {"profile": "Second"}
        request = factory.put(url, data=request_data, content_type='application/json')
        request.user = self.user
        request.activity_user = self.activity_user
        response = ProfileTypeUpdate.as_view()(request, **kwargs)
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn(request_data.get('profile').encode(), response.content)

    def test_ProfileTypeUpdate_with_post(self):
        factory = RequestFactory()
        # first create the record
        ur = reverse('profile_type_add')
        request_data = {"profile": "Trial"}
        req = factory.post(ur, data=request_data, content_type='application/json')
        req.user = self.user
        req.activity_user = self.activity_user
        response = ProfileTypeCreate.as_view()(req)
        kwargs = {"id": 1}
        url = reverse('profile_type_edit', kwargs=kwargs)
        request_data = {"profile": "Second"}
        request = factory.post(url, data=request_data, content_type='application/json')
        request.user = self.user
        request.activity_user = self.activity_user
        response = ProfileTypeUpdate.as_view()(request, **kwargs)
        self.assertTrue(status.is_client_error(response.status_code))

    def test_ProfileTypeDelete(self):
        factory = RequestFactory()
        # first create the record
        ur = reverse('profile_type_add')
        request_data = {"profile": "Trial"}
        req = factory.post(ur, data=request_data, content_type='application/json')
        req.user = self.user
        req.activity_user = self.activity_user
        response = ProfileTypeCreate.as_view()(req)
        # Delete the created record
        kwargs = {"id": 1}
        url = reverse('profile_type_delete', kwargs=kwargs)
        request = factory.delete(url, content_type='application/json')
        response = ProfileTypeDelete.as_view()(request, **kwargs)
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn("success".encode(), response.content)

    def test_ProfileTypeDelete_with_wrong_method(self):
        factory = RequestFactory()
        # first create the record
        ur = reverse('profile_type_add')
        request_data = {"profile": "Trial"}
        req = factory.post(ur, data=request_data, content_type='application/json')
        req.user = self.user
        req.activity_user = self.activity_user
        response = ProfileTypeCreate.as_view()(req)
        # Delete the created record
        kwargs = {"id": 1}
        url = reverse('profile_type_delete', kwargs=kwargs)
        request = factory.put(url, content_type='application/json')
        response = ProfileTypeDelete.as_view()(request, **kwargs)
        self.assertTrue(status.is_client_error(response.status_code))
