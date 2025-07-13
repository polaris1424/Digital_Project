"""
Template code from
https://docs.djangoproject.com/en/4.2/topics/testing/tools/#liveservertestcase
https://docs.djangoproject.com/en/4.2/topics/db/fixtures/

dump database content to a fixture:
manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > testdata.json
credit: https://stackoverflow.com/questions/853796/problems-with-contenttypes-when-loading-a-fixture-in-django

testing:
manage.py test home.tests.frontend.test_search_bar
"""

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

# run python test_hompage.py


class TestSearchBar(StaticLiveServerTestCase):
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

    
    def test_search_bar_has_result(self):
        # login
        self.driver.get(f"{self.live_server_url}/login")
        username_input = self.driver.find_element(By.ID, "id_username")
        password_input = self.driver.find_element(By.ID, "id_password")
        submit_btn = self.driver.find_element(By.TAG_NAME, "button")
        username_input.send_keys("testuser")
        password_input.send_keys("testpassword")
        submit_btn.click()

        name_elem = self.driver.find_element(By.XPATH, "//tbody/tr[1]/td[2]")
        expected_name = name_elem.get_attribute("innerHTML")

        search_bar = self.driver.find_element(By.XPATH, '//*[@id="topbarInputIconLeft"]')
        search_bar.send_keys(expected_name)
        search_btn = self.driver.find_element(By.XPATH, '/html/body/main/div/div[2]/div/button')
        search_btn.click()

        name_elem_after = self.driver.find_element(By.XPATH, "//tbody/tr[1]/td[2]")

        self.assertInHTML(expected_name, name_elem_after.text)
    

    def test_search_bar_has_no_result(self):
        # login
        self.driver.get(f"{self.live_server_url}/login")
        username_input = self.driver.find_element(By.ID, "id_username")
        password_input = self.driver.find_element(By.ID, "id_password")
        submit_btn = self.driver.find_element(By.TAG_NAME, "button")
        username_input.send_keys("testuser")
        password_input.send_keys("testpassword")
        submit_btn.click()

        name_elem = self.driver.find_element(By.XPATH, "//tbody/tr[1]/td[2]")
        expected_name = name_elem.get_attribute("innerHTML")
        self.assertIsNotNone(name_elem)

        search_bar = self.driver.find_element(By.XPATH, '//*[@id="topbarInputIconLeft"]')
        search_btn = self.driver.find_element(By.XPATH, '/html/body/main/div/div[2]/div/button')

        search_bar.send_keys("gibberish")
        search_btn.click()
        try:
            entry_elem_after = self.driver.find_element(By.XPATH, "//tbody/tr[1]")
            # found
            self.assertFalse()
        except:
            # not found
            pass
        #print("!!!!!!!!!!!!!!!!!!!!!!!!!!name_elem", entry_elem_after.text)
        #self.assertEqual(0, len(entry_elem_after))
        
