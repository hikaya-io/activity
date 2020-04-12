# TODO Separate into unauthenticated and authenticated scenarios
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

import time

class FunctionalTests(StaticLiveServerTestCase):
    # TODO add fixture for user data
    fixtures = ['auth_groups.json']

    @classmethod
    def setUpClass(cls):
    # def setUp(cls):
        super().setUpClass()
        cls.selenium = webdriver.firefox.webdriver.WebDriver()
        cls.selenium.implicitly_wait(5)
        cls.wait = WebDriverWait(cls.selenium, 5)

    @classmethod
    def tearDownClass(cls):
    # def tearDown(cls):
        cls.selenium.quit()
        # super().tearDownClass()
        # super().tearDown()

    # @staticmethod
    def login(self, username, password):
        self.selenium.get('http://127.0.0.1:8000')
        # time.sleep(2)
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "login_username"))
        )
        # username_input = self.selenium.find_element_by_id('login_username')
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_id('login_password')
        password_input.send_keys(password)

        password_input.submit()

    # Creates an organization, for a logged in user
    def create_organization(self, org):
        self.selenium.get('http://127.0.0.1:8000/accounts/register/organization')
        # print('Sleeping...')
        time.sleep(1)
        org_name_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "org_name"))
        )

        org_name_input.send_keys(org['name'])

        description_input = self.selenium.find_element_by_id('description')
        description_input.send_keys(org['description'])

        org_url_input = self.selenium.find_element_by_id('org_url')
        org_url_input.send_keys(org['url'])

        location_input = self.selenium.find_element_by_id('location')
        location_input.send_keys(org['location'])

        location_input.submit()



    # Tests that the registering works, and the login with an inactivated email fails
    def test_register(self):
        print('TODO')

    # Test the login using user data from fixtures
    def test_login(self):
        self.selenium.get('http://127.0.0.1:8000')
        assert 'Activity' in self.selenium.title

        self.login('anas', 'hikaya')
        # TODO assertions to check login

    def test_create_organizations(self):
        organizations = [
            {
                'name': 'Test Organization 1',
                'description': 'Testing',
                'url': 'http://testing.com',
                'location': 'Sydney'
            },
            {
                'name': 'Test Organization 2',
                'description': 'Testing',
                'url': 'http://testing-2.com',
                'location': 'Nairobi'
            },
        ]

        self.login('anas', 'hikaya')

        # # Waiting for the panel-dashboard to appear, proof of succesfull login
        self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "panel-dashboard"))
        )
        for org in organizations:
            self.create_organization(org)

        time.sleep(1)