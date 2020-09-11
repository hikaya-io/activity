from django.test import TestCase, Client
from formlibrary.models import Individual, Household
from django.urls import reverse
import datetime
from rest_framework.test import APIClient
from django.contrib.auth.models import User


class IndividualTestCase(TestCase):

    # fixtures = [
    #     'fixtures/tests/trainings.json',
    #     'fixtures/tests/users.json',
    #     'fixtures/tests/activity-users.json',
    # ]

    def setUp(self):
        User.objects.create(username='test', email="test@mail.com", password='password')

        household = Household.objects.create(name="MyHouse", primary_phone='40-29104782')
        individual = Individual.objects.create(
            first_name="Nate", last_name="Test", date_of_birth=datetime.date(2000, 10, 10),
            sex="M", signature=False, description="life", household_id=household)
        individual.save()

        self.client = APIClient()

    def _get_token(self, url, data):
        resp = self.client.get(url)
        print("***resp****")
        print(resp.cookies)
        data['csrfmiddlewaretoken'] = resp.cookies['csrftoken'].value
        return data
        

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

    
    # def test_create_individual_request(self):
        # individual = {
        #     'first_name' : 'test',
        #     # 'last_name' : 'test_last',
        #     'date_of_birth' : '2000-10-10',
        #     'sex' : 'M',
        #     # 'signature' : False,
        #     'description' : 'life',
        #     'id_program' : '1',
        #     'program' : '1'
        # }

        # user = User.objects.get(username='test')
        
        # url = reverse("individual_add", args=['0'])
        # self.client.force_authenticate(self.user)
        
        # resp = self.client.post(url, data=individual)
        # self.assertContains(resp, 200)

        
