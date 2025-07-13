"""
Template code from
https://docs.djangoproject.com/en/4.2/topics/testing/tools/#liveservertestcase
https://docs.djangoproject.com/en/4.2/topics/db/fixtures/

dump database content to a fixture:
manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > testdata.json
credit: https://stackoverflow.com/questions/853796/problems-with-contenttypes-when-loading-a-fixture-in-django

testing:
manage.py test home.tests.frontend.test_view_client
"""

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
import time

# run python test_hompage.py


class TestViewClient(StaticLiveServerTestCase):
    fixtures = ["testdata.json"]

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.driver = WebDriver()
        self.driver.implicitly_wait(30)
        self.driver.set_page_load_timeout(10)

    @classmethod
    def tearDownClass(self):
        # close WebDriver
        self.driver.quit()
        super().tearDownClass()


    
    def test_login_rendered(self):
        self.driver.get(f"{self.live_server_url}/login")
        html = self.driver.find_element(By.TAG_NAME, "html")
        self.assertIn("Welcome to Senψ", html.text)
    

    def test_login(self):
        # login
        self.driver.get(f"{self.live_server_url}/login")
        username_input = self.driver.find_element(By.ID, "id_username")
        password_input = self.driver.find_element(By.ID, "id_password")
        submit_btn = self.driver.find_element(By.TAG_NAME, "button")
        username_input.send_keys("testuser")
        password_input.send_keys("testpassword")
        submit_btn.click()

        html = self.driver.find_element(By.TAG_NAME, "html")
        self.assertIn("Client List", html.text)

        # logout
        self.driver.get(f"{self.live_server_url}/logout")


    def test_view_client_rendered(self):
        # login
        self.driver.get(f"{self.live_server_url}/login")
        username_input = self.driver.find_element(By.ID, "id_username")
        password_input = self.driver.find_element(By.ID, "id_password")
        submit_btn = self.driver.find_element(By.TAG_NAME, "button")
        username_input.send_keys("testuser")
        password_input.send_keys("testpassword")
        submit_btn.click()

        view_button = self.driver.find_element(By.XPATH, "//tbody/tr/td/button[1]")
        self.assertIsNotNone(view_button)
        view_button.click()

        title = self.driver.find_element(By.XPATH, "//h2")
        self.assertIsNotNone(title)
        self.assertInHTML("View Client", title.text)
