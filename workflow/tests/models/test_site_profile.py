from django.test import TestCase
from workflow.models import (
    Country,
    Office,
    Organization,
    Province,
    SiteProfile,
)


class SiteProfileTestCase(TestCase):

    fixtures = ['fixtures/tests/organization.json', 'fixtures/tests/profiletypes.json']

    def setUp(self):
        new_organization = Organization.objects.create(name="Activity")
        new_organization.save()
        get_organization = Organization.objects.get(name="Activity")
        new_country = Country.objects.create(
            country="testcountry", organization=get_organization)
        new_country.save()
        get_country = Country.objects.get(country="testcountry")
        new_province = Province.objects.create(
            name="testprovince", country=get_country)
        new_province.save()
        get_province = Province.objects.get(name="testprovince")
        new_office = Office.objects.create(
            name="testoffice", province=new_province)
        new_office.save()
        get_office = Office.objects.get(name="testoffice")
        new_community = SiteProfile.objects.create(
            name="testcommunity", country=get_country, office=get_office,
            province=get_province)
        new_community.save()

    def test_community_exists(self):
        """Check for SiteProfile Object"""
        get_community = SiteProfile.objects.get(name="testcommunity")
        self.assertEqual(SiteProfile.objects.filter(
            id=get_community.id).count(), 1)
