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


driver.quit()
