from selenium import webdriver

# Connect to remote PhantomJS interface ran in docker container
# driver = webdriver.Remote(
#     command_executor='http://127.0.0.1:8910',
#     desired_capabilities=DesiredCapabilities.PHANTOMJS
# )

# Local usage of PhantomJS
# driver = webdriver.PhantomJS()
# Local usage of Firefox
driver = webdriver.Firefox()

driver.get('http://localhost:8000')
assert 'Activity' in driver.title

# Fill login form and submit it
username_input = driver.find_element_by_id('login_username')
username_input.send_keys('anas')
password_input = driver.find_element_by_id('login_password')
password_input.send_keys('hikaya')

password_input.submit()

# TODO check that I am redirected to create a new organization

driver.quit()
