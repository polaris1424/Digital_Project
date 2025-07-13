"""
Template code from
https://docs.djangoproject.com/en/4.2/topics/testing/tools/#liveservertestcase
https://docs.djangoproject.com/en/4.2/topics/db/fixtures/

dump database content to a fixture:
manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > testdata.json
credit: https://stackoverflow.com/questions/853796/problems-with-contenttypes-when-loading-a-fixture-in-django

testing:
manage.py test home.tests.frontend.test_add_client
"""

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains

import uuid
import time

# run python test_hompage.py


class TestAddClient(StaticLiveServerTestCase):
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


    def test_add_client_page_rendered(self):
        # login
        self.driver.get(f"{self.live_server_url}/login")
        username_input = self.driver.find_element(By.ID, "id_username")
        password_input = self.driver.find_element(By.ID, "id_password")
        submit_btn = self.driver.find_element(By.TAG_NAME, "button")
        username_input.send_keys("testuser")
        password_input.send_keys("testpassword")
        submit_btn.click()

        add_new_client_button = self.driver.find_element(By.XPATH, "/html/body/main/div/div[2]/button")
        add_new_client_button.click()

        html = self.driver.find_element(By.TAG_NAME, "html")
        self.assertIn("<h2>Add Client</h2>", html.get_attribute("innerHTML"))


    """
    def test_add_client(self):
        #login
        self.driver.get(f"{self.live_server_url}/login")
        username_input = self.driver.find_element(By.ID, "id_username")
        password_input = self.driver.find_element(By.ID, "id_password")
        submit_btn = self.driver.find_element(By.TAG_NAME, "button")
        username_input.send_keys("testuser")
        password_input.send_keys("testpassword")
        submit_btn.click()

        add_new_client_button = self.driver.find_element(By.XPATH, "/html/body/main/div/div[2]/button")
        add_new_client_button.click()


        # username
        expected_username = 'john123'
        username = self.driver.find_element(By.XPATH, '//*[@id="client_name"]')
        username.send_keys(expected_username)
        # gender
        select_gender_elem = self.driver.find_element(By.XPATH, '//*[@id="client_gender"]')
        select_gender = Select(select_gender_elem)
        select_gender.select_by_value("male")
        # birthday
        expected_birthday = '1990-01-02'
        self.driver.execute_script("document.evaluate('//*[@id=\"client_birthday\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.value=\"1990-01-02\";")
        # title
        select_title_elem = self.driver.find_element(By.XPATH, '//*[@id="client_title"]')
        select_title = Select(select_title_elem)
        select_title.select_by_value("Mr.")
        # firstname
        random_firstname = str(uuid.uuid4())
        firstname = self.driver.find_element(By.XPATH, '//*[@id="client_first_name"]')
        firstname.send_keys(random_firstname)
        # lastname
        random_lastname = str(uuid.uuid4())
        lastname = self.driver.find_element(By.XPATH, '//*[@id="client_last_name"]')
        lastname.send_keys(random_lastname)
        # facebookid
        random_facebookid = str(uuid.uuid4())
        facebook_id = self.driver.find_element(By.XPATH, '//*[@id="client_facebook_id"]')
        facebook_id.send_keys(random_facebookid)
        # twitter id
        random_twitter_id = str(uuid.uuid4())
        twitter_id = self.driver.find_element(By.XPATH, '//*[@id="client_twitter_id"]')
        twitter_id.send_keys(random_twitter_id)
        # aware_id
        expected_aware_id = '1cd23312-6180-448d-87a5-2004fb9432b2'
        aware_id = self.driver.find_element(By.XPATH, '//*[@id="client_device_id"]')
        aware_id.send_keys(expected_aware_id)

        # submit_button
        submit_btn = self.driver.find_element(By.XPATH, "//*[@type='submit']")
        # https://stackoverflow.com/questions/41744368/scrolling-to-element-using-webdriver
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        # https://stackoverflow.com/questions/71947784/what-does-webdriverwaitdriver-20-mean
        # click submit button
        time.sleep(2)
        submit_btn.click()
        time.sleep(2)
        #WebDriverWait(self.driver, 20).until(expected_conditions.element_to_be_clickable((By.XPATH, "//*[@type='submit']"))).click()

        self.driver.get(f"{self.live_server_url}/homePage")
        client_table = self.driver.find_element(By.XPATH, '/html/body/main/div/div[3]/div/div/div[1]/table/tbody')
        client_list = client_table.find_elements(By.XPATH, '*')
        for client in client_list:
            cells = client.find_elements(By.TAG_NAME, 'td')
            if (cells[1] == expected_username):
                # view button
                btn = cells[5].find_element(By.XPATH, 'button[1]')
                btn.click()
                break

        html = self.driver.find_element(By.TAG_NAME, 'html')
        self.assertInHTML('View Client', html.text)
        # username
        username = self.driver.find_element(By.XPATH, '//*[@id="client_name"]')
        self.assertEquals(expected_username, username.get_attribute('value'))
        # firstname
        firstname = self.driver.find_element(By.XPATH, '//*[@id="client_first_name"]')
        self.assertEquals(random_firstname, firstname.get_attribute('value'))
        # lastname
        lastname = self.driver.find_element(By.XPATH, '//*[@id="client_last_name"]')
        self.assertEquals(random_lastname, lastname.get_attribute('value'))
        # gender
        gender = self.driver.find_element(By.XPATH, '//*[@id="client_gender"]')
        self.assertEquals('male', gender.get_attribute('value'))
        # birthday
        birthday = self.driver.find_element(By.XPATH, '//*[@id="client_birthday"]')
        self.assertEquals(expected_birthday, birthday.value)
        # title
        title = self.driver.find_element(By.XPATH, '//*[@id="client_title"]')
        self.assertEquals('Mr.', title.get_attribute('value'))
        # twitter id
        twitter_id = self.driver.find_element(By.XPATH, '//*[@id="client_twitter_id"]')
        self.assertEquals(random_twitter_id, twitter_id.get_attribute('value'))
        # facebook id
        facebook_id = self.driver.find_element(By.XPATH, '//*[@id="client_facebook_id"]')
        self.assertEquals(random_facebookid, facebook_id.get_attribute('value'))
        # aware id
        aware_id = self.driver.find_element(By.XPATH, '//*[@id="client_device_id"]')
        self.assertEquals(expected_aware_id, aware_id.get_attribute('value'))
    """
        


