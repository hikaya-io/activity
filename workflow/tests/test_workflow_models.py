#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.test import TestCase
from workflow.models import (
    Organization, Program, Country, Province, ProjectAgreement, Sector,
    ProjectComplete, ProjectType, SiteProfile, Office, Benchmarks, Budget,
    Documentation, Checklist, ProjectStatus
)

class ProjectStatusTestCase(TestCase):


    def setUp(self):
        new_project_status = ProjectStatus.objects.create(name="project status")
        new_project_status.save()

    def test_project_status_creation(self):
        """Check for ProjectStatus Object creation"""
        get_project_status = ProjectStatus.objects.get(name="project status")
        self.assertTrue(isinstance(get_project_status, ProjectStatus))
        self.assertTrue(get_project_status.__str__(), get_project_status.name)

class DocumentationTestCase(TestCase):


    def setUp(self):
        new_documentation = Documentation.objects.create(name="document created", description="documentation test")
        new_documentation.save()

    def test_documenation_creation(self):
        """Check Documentation Object creation"""
        get_documentation =Documentation.objects.get(name="document created")
        self.assertTrue(isinstance(get_documentation, Documentation))
        self.assertTrue(get_documentation.__str__(), get_documentation.name)

class ChecklistTestCase(TestCase):


    fixtures = ['fixtures/sectors.json', 'fixtures/projecttype.json']
    def setUp(self):   
        # load from fixtures
        get_project_type = ProjectType.objects.get(id='1')
        get_sector = Sector.objects.get(id='2')
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
            name="testoffice", province=get_province)
        new_office.save()
        get_office = Office.objects.get(name="testoffice")
        new_program = Program.objects.create(name="testprogram")
        new_program.save()
        new_program.country.add(get_country)
        get_program = Program.objects.get(name="testprogram")
        new_agreement = ProjectAgreement.objects.create(
            program=get_program,
            project_name="testproject",
            project_type=get_project_type, activity_code="111222",
            office=get_office, sector=get_sector)
        new_agreement.save()
        get_agreement = ProjectAgreement.objects.get(project_name="testproject")
        new_checklist = Checklist.objects.create(name="test checklist created", country=get_country, agreement=get_agreement)
        new_checklist.save();
        new_sector = Sector.objects.create(sector="new sector", create_date=None)
        new_sector.save()

    def test_sector_creation(self):
        """Test sector creation with null create_date"""
        get_sector = Sector.objects.get(sector="new sector")
        self.assertTrue(isinstance(get_sector, Sector))
        self.assertTrue(get_sector.__str__(), get_sector.sector)


    def test_checklist_creation(self):
        """Check for Checklist Object creation"""
        get_checklist =Checklist.objects.get(name="test checklist created")
        self.assertTrue(isinstance(get_checklist, Checklist))
        self.assertTrue(get_checklist.__str__(), get_checklist.agreement)


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

    def test_community_creation(self):
        """Test if SiteProfile Object is created"""
        get_community = SiteProfile.objects.get(name="testcommunity")
        self.assertTrue(isinstance(get_community, SiteProfile))
        self.assertTrue(get_community.__str__(), get_community.name)

    def test_community_exists(self):
        """Check for SiteProfile Object"""
        get_community = SiteProfile.objects.get(name="testcommunity")
        self.assertEqual(SiteProfile.objects.filter(
            id=get_community.id).count(), 1)


class AgreementTestCase(TestCase):

    fixtures = ['fixtures/tests/projecttype.json', 'fixtures/tests/sectors.json']

    def setUp(self):
        new_organization = Organization.objects.create(name="Activity")
        new_organization.save()
        get_organization = Organization.objects.get(name="Activity")
        new_country = Country.objects.create(
            country="testcountry", organization=get_organization)
        new_country.save()
        get_country = Country.objects.get(country="testcountry")
        new_program = Program.objects.create(name="testprogram")
        new_program.save()
        new_program.country.add(get_country)
        get_program = Program.objects.get(name="testprogram")
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
        get_community = SiteProfile.objects.get(name="testcommunity")
        # load from fixtures
        get_project_type = ProjectType.objects.get(id='1')
        get_sector = Sector.objects.get(id='2')
        new_agreement = ProjectAgreement.objects.create(
            program=get_program,
            project_name="testproject",
            project_type=get_project_type, activity_code="111222",
            office=get_office, sector=get_sector)
        new_agreement.save()
        new_agreement.site.add(get_community)

        new_benchmarks = Benchmarks.objects.create(
            percent_complete="1234", percent_cumulative="14",
            agreement=new_agreement,
            description = "benchmark desc"
            )
        new_benchmarks.save()

        new_budget = Budget.objects.create(
            contributor="testbudget",
            description_of_contribution="new_province", proposed_value="24",
            agreement=new_agreement)
        new_budget.save()

    def test_Benchmarks_saving(self):
        """Test wether new benchmarks are saved"""
        get_benchmark = Benchmarks.objects.get(percent_complete="1234")
        self.assertTrue(isinstance(get_benchmark, Benchmarks))
        self.assertTrue(get_benchmark.__str__(), get_benchmark.description)


    def test_Agreement_creation(self):
        """Test if Agreement Object is created"""
        get_agreement = ProjectAgreement.objects.get(
            project_name="testproject")
        self.assertTrue(isinstance(get_agreement, ProjectAgreement))
        self.assertTrue(get_agreement.__str__(), get_agreement.project_name)


    def test_agreement_exists(self):
        """Check for Agreement object"""
        get_agreement = ProjectAgreement.objects.get(
            project_name="testproject")
        self.assertEqual(ProjectAgreement.objects.filter(
            id=get_agreement.id).count(), 1)

    def test_benchmark_creation(self):
        """Test if Benchmarks Object is created"""
        get_benchmark = Benchmarks.objects.get(percent_complete="1234")
        self.assertTrue(isinstance(get_benchmark, Benchmarks))

    def test_benchmark_exists(self):
        """Check for Benchmark object"""
        get_benchmark = Benchmarks.objects.get(percent_complete="1234")
        self.assertEqual(Benchmarks.objects.filter(
            id=get_benchmark.id).count(), 1)

    def test_Budget_creation(self):
        """Test if Budget Object is created"""
        get_budget = Budget.objects.get(contributor="testbudget")
        self.assertTrue(isinstance(get_budget, Budget))
        self.assertTrue(get_budget.__str__(), get_budget.contributor)

    def test_budget_exists(self):
        """Check for Budget object"""
        get_budget = Budget.objects.get(contributor="testbudget")
        self.assertEqual(Budget.objects.filter(id=get_budget.id).count(), 1)


class CompleteTestCase(TestCase):

    fixtures = ['fixtures/tests/projecttype.json', 'fixtures/tests/sectors.json']

    def setUp(self):
        new_organization = Organization.objects.create(name="Activity")
        new_organization.save()
        get_organization = Organization.objects.get(name="Activity")
        new_country = Country.objects.create(
            country="testcountry", organization=get_organization)
        new_country.save()
        get_country = Country.objects.get(country="testcountry")
        new_program = Program.objects.create(name="testprogram")
        new_program.save()
        new_program.country.add(get_country)
        get_program = Program.objects.get(name="testprogram")
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
        get_community = SiteProfile.objects.get(name="testcommunity")
        # load from fixtures
        get_project_type = ProjectType.objects.get(id='1')
        get_sector = Sector.objects.get(id='2')
        new_agreement = ProjectAgreement.objects.create(
            program=get_program,
            project_name="testproject",
            project_type=get_project_type, activity_code="111222",
            office=get_office, sector=get_sector)
        new_agreement.save()
        new_agreement2 = ProjectAgreement.objects.create(
            program=get_program,
            project_name="testproject2",
            project_type=get_project_type, activity_code="111222",
            office=get_office, sector=get_sector,
            total_estimated_budget = None,
            mc_estimated_budget = None,
            local_total_estimated_budget = None,
            local_mc_estimated_budget = None
            )
        new_agreement2.save()
        new_agreement2.site.add(get_community)
        new_agreement.site.add(get_community)
        get_agreement = ProjectAgreement.objects.get(
            project_name="testproject")
        get_agreement2 = ProjectAgreement.objects.get(
            project_name="testproject2")
        new_complete = ProjectComplete.objects.create(
            program=get_program, project_name="testproject",
            activity_code="111222", office=get_office, on_time=True,
            community_handover=1, project_agreement=get_agreement,
            estimated_budget = None, actual_budget = None, total_cost = None,
            agency_cost = None, local_total_cost = None, local_agency_cost = None
            )
        new_complete2 = ProjectComplete.objects.create(
            program=get_program, project_name="testproject2",
            activity_code="111222", office=get_office, on_time=True,
            community_handover=1, project_agreement=get_agreement2)
        new_complete.save()
        new_complete2.save()

    def test_complete_creation(self):
        """Test if ProjectComplete Object is created with defaults set to None"""
        get_complete = ProjectComplete.objects.get(project_name="testproject")
        self.assertTrue(isinstance(get_complete, ProjectComplete))
        self.assertTrue(get_complete.__str__(), get_complete.project_name)

    def test_complete_creation_with_defaults_for_project_agreement(self):
        """Test if ProjectComplete Object with defaults for ProjectAgreement Object is created"""
        get_complete2 = ProjectComplete.objects.get(project_name="testproject2")
        self.assertTrue(isinstance(get_complete2, ProjectComplete))
        self.assertTrue(get_complete2.__str__(), get_complete2.project_name)

    def test_complete_exists(self):
        """Check for Complete object"""
        get_complete = ProjectComplete.objects.get(project_name="testproject")
        self.assertEqual(ProjectComplete.objects.filter(
            id=get_complete.id).count(), 1)
