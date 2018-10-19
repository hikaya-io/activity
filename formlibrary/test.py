from django.test import TestCase
from workflow.models import Program, Country, Province,ProjectAgreement, Sector, ProjectType, SiteProfile, Office
from formlibrary.models import TrainingAttendance, Distribution, Beneficiary
from datetime import datetime


class TrainingAttendanceTestCase(TestCase):

    def setUp(self):
        new_program = Program.objects.create(name="testprogram")
        new_program.save()
        get_program = Program.objects.get(name="testprogram")
        new_training = TrainingAttendance.objects.create(training_name="testtraining", program=get_program,
                                                           implementer = "34",
                                                           reporting_period = "34",
                                                           total_participants = "34",
                                                           location = "34",
                                                           community = "34",
                                                           training_duration = "34",
                                                           start_date = "34",
                                                           end_date = "34",
                                                           trainer_name = "34",
                                                           trainer_contact_num = "34",
                                                           form_filled_by = "34",
                                                           form_filled_by_contact_num = "34",
                                                           total_male = "34",
                                                           total_female = "34",
                                                           total_age_0_14_male = "34",
                                                           total_age_0_14_female = "34",
                                                           total_age_15_24_male = "34",
                                                           total_age_15_24_female = "34",
                                                           total_age_25_59_male = "34"
                                                         )
        new_training.save()

    def test_training_exists(self):
        """Check for Training object"""
        get_training = TrainingAttendance.objects.get(training_name="testtraining")
        self.assertEqual(TrainingAttendance.objects.filter(id=get_training.id).count(), 1)


class DistributionTestCase(TestCase):

    fixtures = ['fixtures/projecttype.json','fixtures/sectors.json']

    def setUp(self):
        new_program = Program.objects.create(name="testprogram")
        new_program.save()
        get_program = Program.objects.get(name="testprogram")
        new_country = Country.objects.create(country="testcountry")
        new_country.save()
        get_country = Country.objects.get(country="testcountry")
        new_province = Province.objects.create(name="testprovince", country=get_country)
        new_province.save()
        get_province = Province.objects.get(name="testprovince")
        new_office = Office.objects.create(name="testoffice",province=new_province)
        new_office.save()
        get_office = Office.objects.get(name="testoffice")
        #create project agreement -- and load from fixtures
        new_community = SiteProfile.objects.create(name="testcommunity", country=get_country, office=get_office,province=get_province)
        new_community.save()
        get_community = SiteProfile.objects.get(name="testcommunity")
        get_project_type = ProjectType.objects.get(id='1')
        get_sector = Sector.objects.get(id='2')
        new_agreement = ProjectAgreement.objects.create(program=get_program, project_name="testproject", project_type=get_project_type,
                                                        activity_code="111222", office=get_office,
                                                        sector=get_sector)
        new_agreement.save()
        new_agreement.site.add(get_community)
        get_agreement = ProjectAgreement.objects.get(project_name="testproject")
        new_distribution = Distribution.objects.create(distribution_name="testdistribution", program=get_program,
                                                            initiation=get_agreement,
                                                            office_code=get_office,
                                                            distribution_indicator = "34",
                                                            distribution_implementer = "34",
                                                            reporting_period = "34",
                                                            province=get_province,
                                                            total_beneficiaries_received_input = "34",
                                                            distribution_location = "testlocation",
                                                            input_type_distributed = "testinputtype",
                                                            distributor_name_and_affiliation = "testdistributorperson",
                                                            distributor_contact_number = "1-dis-tri-bute",
                                                            start_date = datetime(2015, 8, 4, 12, 30, 45),
                                                            end_date = datetime(2015, 9, 5, 12, 30, 45),
                                                            form_filled_by = "test_form_filler",
                                                            form_filled_by_position = "testdistributionmanager",
                                                            form_filled_by_contact_num = "1-888-dst-rbut",
                                                            form_filled_date = datetime(2016, 6, 1, 12, 30, 45),
                                                            form_verified_by = "test_form_verifier",
                                                            form_verified_by_position = "testdistributionmanager",
                                                            form_verified_by_contact_num = "1-888-dst-rbut",
                                                            form_verified_date = datetime(2016, 6, 2, 12, 30, 45),
                                                            total_received_input = "34",
                                                            total_male = "34",
                                                            total_female = "34",
                                                            total_age_0_14_male = "34",
                                                            total_age_0_14_female = "34",
                                                            total_age_15_24_male = "34",
                                                            total_age_15_24_female = "34",
                                                            total_age_25_59_male = "34",
                                                            total_age_25_59_female = "34"
                                                         )
        new_distribution.save()

    def test_distribution_exists(self):
        """Check for Distribution object"""
        get_distribution = Distribution.objects.get(distribution_name="testdistribution")
        self.assertEqual(Distribution.objects.filter(id=get_distribution.id).count(), 1)


class BeneficiaryTestCase(TestCase):

    def setUp(self):
        new_program = Program.objects.create(name="testprogram")
        new_program.save()
        get_program = Program.objects.get(name="testprogram")
        new_training = TrainingAttendance.objects.create(training_name="testtraining", program=get_program)
        new_training.save()
        get_training = TrainingAttendance.objects.get(training_name="testtraining")
        new_benny = Beneficiary.objects.create(beneficiary_name="Joe Test", father_name="Mr Test", age="42", gender="male", signature=False,remarks="life")
        new_benny.training.add(new_training)
        new_benny.save()

    def test_beneficiary_exists(self):
        """Check for Benny object"""
        get_benny = Beneficiary.objects.get(beneficiary_name="Joe Test")
        self.assertEqual(Beneficiary.objects.filter(id=get_benny.id).count(), 1)
