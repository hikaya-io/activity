from django.test import TestCase
from workflow.models import Organization, Program, Country, Province, ProjectAgreement, Sector, ProjectComplete, ProjectType, SiteProfile, Office, Monitor, Benchmarks, Budget


class SiteProfileTestCase(TestCase):

    fixtures = ['fixtures/organization.json','fixtures/profiletypes.json']

    def setUp(self):
        new_organization = Organization.objects.create(name="tola")
        new_organization.save()
        get_organization = Organization.objects.get(name="tola")
        new_country = Country.objects.create(country="testcountry", organization=get_organization)
        new_country.save()
        get_country = Country.objects.get(country="testcountry")
        new_province = Province.objects.create(name="testprovince", country=get_country)
        new_province.save()
        get_province = Province.objects.get(name="testprovince")
        new_office = Office.objects.create(name="testoffice",province=new_province)
        new_office.save()
        get_office = Office.objects.get(name="testoffice")
        new_community = SiteProfile.objects.create(name="testcommunity", country=get_country, office=get_office,province=get_province)
        new_community.save()

    def test_community_exists(self):
        """Check for SiteProfile Object"""
        get_community = SiteProfile.objects.get(name="testcommunity")
        self.assertEqual(SiteProfile.objects.filter(id=get_community.id).count(), 1)


class AgreementTestCase(TestCase):

    fixtures = ['fixtures/projecttype.json','fixtures/sectors.json']

    def setUp(self):
        new_organization = Organization.objects.create(name="tola")
        new_organization.save()
        get_organization = Organization.objects.get(name="tola")
        new_country = Country.objects.create(country="testcountry", organization=get_organization)
        new_country.save()
        get_country = Country.objects.get(country="testcountry")
        new_program = Program.objects.create(name="testprogram")
        new_program.save()
        new_program.country.add(get_country)
        get_program = Program.objects.get(name="testprogram")
        new_province = Province.objects.create(name="testprovince", country=get_country)
        new_province.save()
        get_province = Province.objects.get(name="testprovince")
        new_office = Office.objects.create(name="testoffice",province=new_province)
        new_office.save()
        get_office = Office.objects.get(name="testoffice")
        new_community = SiteProfile.objects.create(name="testcommunity", country=get_country, office=get_office,province=get_province)
        new_community.save()
        get_community = SiteProfile.objects.get(name="testcommunity")
        #load from fixtures
        get_project_type = ProjectType.objects.get(id='1')
        get_sector = Sector.objects.get(id='2')
        new_agreement = ProjectAgreement.objects.create(program=get_program, project_name="testproject", project_type=get_project_type,
                                                      activity_code="111222",office=get_office,
                                                      sector=get_sector)
        new_agreement.save()
        new_agreement.site.add(get_community)

        new_benchmarks = Benchmarks.objects.create(percent_complete="1234", percent_cumulative="14",agreement=new_agreement)
        new_benchmarks.save()

        new_budget = Budget.objects.create(contributor="testbudget", description_of_contribution="new_province", proposed_value="24", agreement=new_agreement)
        new_budget.save()

        new_monitor = Monitor.objects.create(responsible_person="testmonitor", frequency="freq", type="24", agreement=new_agreement)
        new_monitor.save()

    def test_agreement_exists(self):
        """Check for Agreement object"""
        get_agreement = ProjectAgreement.objects.get(project_name="testproject")
        self.assertEqual(ProjectAgreement.objects.filter(id=get_agreement.id).count(), 1)

    def test_benchmark_exists(self):
        """Check for Benchmark object"""
        get_benchmark = Benchmarks.objects.get(percent_complete="1234")
        self.assertEqual(Benchmarks.objects.filter(id=get_benchmark.id).count(), 1)

    def test_budget_exists(self):
        """Check for Budget object"""
        get_budget = Budget.objects.get(contributor="testbudget")
        self.assertEqual(Budget.objects.filter(id=get_budget.id).count(), 1)

    def test_monitor_exists(self):
        """Check for Monitor object"""
        get_monitor = Monitor.objects.get(responsible_person="testmonitor")
        self.assertEqual(Monitor.objects.filter(id=get_monitor.id).count(), 1)


class CompleteTestCase(TestCase):

    fixtures = ['fixtures/projecttype.json','fixtures/sectors.json']

    def setUp(self):
        new_organization = Organization.objects.create(name="tola")
        new_organization.save()
        get_organization = Organization.objects.get(name="tola")
        new_country = Country.objects.create(country="testcountry", organization=get_organization)
        new_country.save()
        get_country = Country.objects.get(country="testcountry")
        new_program = Program.objects.create(name="testprogram")
        new_program.save()
        new_program.country.add(get_country)
        get_program = Program.objects.get(name="testprogram")
        new_province = Province.objects.create(name="testprovince", country=get_country)
        new_province.save()
        get_province = Province.objects.get(name="testprovince")
        new_office = Office.objects.create(name="testoffice",province=new_province)
        new_office.save()
        get_office = Office.objects.get(name="testoffice")
        new_community = SiteProfile.objects.create(name="testcommunity", country=get_country, office=get_office,province=get_province)
        new_community.save()
        get_community = SiteProfile.objects.get(name="testcommunity")
        #load from fixtures
        get_project_type = ProjectType.objects.get(id='1')
        get_sector = Sector.objects.get(id='2')
        new_agreement = ProjectAgreement.objects.create(program=get_program, project_name="testproject", project_type=get_project_type,
                                                        activity_code="111222", office=get_office,
                                                        sector=get_sector)
        new_agreement.save()
        new_agreement.site.add(get_community)
        get_agreement = ProjectAgreement.objects.get(project_name="testproject")
        new_complete = ProjectComplete.objects.create(program=get_program, project_name="testproject",
                                                      activity_code="111222",office=get_office,on_time=True,
                                                       community_handover=1, project_agreement=get_agreement)
        new_complete.save()

    def test_complete_exists(self):
        """Check for Complete object"""
        get_complete = ProjectComplete.objects.get(project_name="testproject")
        self.assertEqual(ProjectComplete.objects.filter(id=get_complete.id).count(), 1)

