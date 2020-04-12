import time
from selenium import webdriver

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Connect to remote PhantomJS interface ran in docker container
# driver = webdriver.Remote(
#     command_executor='http://127.0.0.1:8910',
#     desired_capabilities=DesiredCapabilities.PHANTOMJS
# )

# Local usage of PhantomJS
# driver = webdriver.PhantomJS()
# Local usage of Firefox
driver = webdriver.Firefox()

# https://selenium-python.readthedocs.io/waits.html
wait = WebDriverWait(driver, 5)

driver.get('http://localhost:8000')
assert 'Activity' in driver.title

# Fill login form and submit it
username_input = driver.find_element_by_id('login_username')
username_input.send_keys('anas')
password_input = driver.find_element_by_id('login_password')
password_input.send_keys('hikaya')

password_input.submit()

# TODO check that I am redirected to create a new organization
# TODO create multiple organizations and switch between them, check the title
# TODO refactor organization creation
org_name_input = wait.until(
    EC.presence_of_element_located((By.ID, "org_name"))
)
# org_name_input = driver.find_element_by_id('org_name')
org_name_input.send_keys('Test Organization')

description_input = driver.find_element_by_id('description')
description_input.send_keys('This is a test organization created using Selenium')

org_url_input = driver.find_element_by_id('org_url')
org_url_input.send_keys('https://test-organization.com')

location_input = driver.find_element_by_id('location')
location_input.send_keys('Wonderland')

# Check that the rendered slugified Activity URL is right
driver.get('http://localhost:8000/accounts/register/organization')
org_name_input = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.ID, "org_name"))
)
# org_name_input = driver.find_element_by_id('org_name')
org_name_input.send_keys('Test Organization 2')

description_input = driver.find_element_by_id('description')
description_input.send_keys('This is the second test organization created using Selenium')

org_url_input = driver.find_element_by_id('org_url')
org_url_input.send_keys('https://test-organization-2.com')

location_input = driver.find_element_by_id('location')
location_input.send_keys('Wonderland 2')

location_input.submit()

# Wait for the last element to be created and redirected to the home dashboard

driver.quit()
