#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User

from workflow.views import (
 GetLevel1DependantData,FundCodeCreate,FundCodeUpdate,FundCodeDelete,FundCodeList,list_workflow_level1,
 GetCountries,service_json,OfficeView, ProfileTypeCreate, ProfileTypeList, ProfileTypeDelete,ProfileTypeUpdate
 )

from workflow.models import ActivityUser, Organization

class ProgramViewTestCase(TestCase):


    fixtures = ['fixtures/indicatortype.json', 'fixtures/sectors.json']
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
                
    def test_list_workflow_level1(self):
        factory = RequestFactory()
        request = factory.get('level1_list')
        request.user = self.user
        request.activity_user = self.activity_user
        response = list_workflow_level1(request)
        self.assertEqual(response.status_code, 200)

    def test_GetLevel1DependantData(self):
        factory = RequestFactory()
        url = reverse('level1_dependant_data')
        request = factory.get(url)
        response = GetLevel1DependantData.as_view()(request)
        self.assertEqual(response.status_code, 200)

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
        request_data = { "name": "Trial"}
        request = factory.post(url, data=request_data, content_type='application/json')
        request.user = self.user
        request.activity_user = self.activity_user
        response = FundCodeCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_FundCodeUpdate(self):
        factory = RequestFactory()
        # first create the record
        ur = reverse('fund_code_add')
        request_data = { "name": "Trial"}
        req = factory.post(ur, data=request_data, content_type='application/json')
        req.user = self.user
        req.activity_user = self.activity_user
        response = FundCodeCreate.as_view()(req)

        kwargs={"id": 1}
        url = reverse('fund_code_edit', kwargs=kwargs)
        request_data = { "name": "Second"}
        request = factory.put(url, data=request_data, content_type='application/json')
        request.user = self.user
        request.activity_user = self.activity_user
        response = FundCodeUpdate.as_view()(request, **kwargs)
        self.assertEqual(response.status_code, 200)


    def test_FundCodeDelete(self):
        factory = RequestFactory()
        # first create the record
        ur = reverse('fund_code_add')
        request_data = { "name": "Trial"}
        req = factory.post(ur, data=request_data, content_type='application/json')
        req.user = self.user
        req.activity_user = self.activity_user
        response = FundCodeCreate.as_view()(req)

        # Delete the created record
        kwargs = {"id":1}
        url = reverse('fund_code_delete', kwargs=kwargs)
        request = factory.delete(url, content_type='application/json')
        response = FundCodeDelete.as_view()(request, **kwargs)
        self.assertEqual(response.status_code, 200)

    def test_FundCodeList(self):
        factory = RequestFactory()
        url = reverse('fund_code_list')
        request = factory.get(url)
        request.user = self.user
        request.activity_user =self.activity_user
        response = FundCodeList.as_view()(request)
        self.assertEqual(response.status_code, 200)

class CountriesTestCase(TestCase):


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

    def test_GetCountries(self):
        factory = RequestFactory()
        url = reverse('get_countries')
        request = factory.get(url)
        request.user = self.user
        request.activity_user = self.activity_user
        response = GetCountries.as_view()(request)
        self.assertEqual(response.status_code, 200)

class ProfileTypeTestCase(TestCase):

    
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
        request_data = { "profile": "Trial"}
        request = factory.post(url, data=request_data, content_type='application/json')
        request.user = self.user
        request.activity_user = self.activity_user
        response = ProfileTypeCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_ProfileTypeList(self):
        factory = RequestFactory()
        url = reverse('profile_type_list')
        request = factory.get(url)
        request.user = self.user
        request.activity_user =self.activity_user
        response = ProfileTypeList.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_ProfileTypeUpdate(self):
        factory = RequestFactory()
        # first create the record
        ur = reverse('profile_type_add')
        request_data = { "profile": "Trial"}
        req = factory.post(ur, data=request_data, content_type='application/json')
        req.user = self.user
        req.activity_user = self.activity_user
        response = ProfileTypeCreate.as_view()(req)

        kwargs={"id": 1}
        url = reverse('profile_type_edit', kwargs=kwargs)
        request_data = { "profile": "Second"}
        request = factory.put(url, data=request_data, content_type='application/json')
        request.user = self.user
        request.activity_user = self.activity_user
        response = ProfileTypeUpdate.as_view()(request, **kwargs)
        self.assertEqual(response.status_code, 200)

    def test_ProfileTypeDelete(self):
        factory = RequestFactory()
        # first create the record
        ur = reverse('profile_type_add')
        request_data = { "profile": "Trial"}
        req = factory.post(ur, data=request_data, content_type='application/json')
        req.user = self.user
        req.activity_user = self.activity_user
        response = ProfileTypeCreate.as_view()(req)

        # Delete the created record
        kwargs = {"id":1}
        url = reverse('profile_type_delete', kwargs=kwargs)
        request = factory.delete(url, content_type='application/json')
        response = ProfileTypeDelete.as_view()(request, **kwargs)
        self.assertEqual(response.status_code, 200)
