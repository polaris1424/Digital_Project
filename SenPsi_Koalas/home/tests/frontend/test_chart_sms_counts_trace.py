"""
Template code from
https://docs.djangoproject.com/en/4.2/topics/testing/tools/#liveservertestcase
https://docs.djangoproject.com/en/4.2/topics/db/fixtures/

dump database content to a fixture:
manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > testdata.json
credit: https://stackoverflow.com/questions/853796/problems-with-contenttypes-when-loading-a-fixture-in-django

testing:
manage.py test home.tests.frontend.test_chart_sms_counts_trace
"""

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchElementException
import time



class TestChartSMSCountsTrace(StaticLiveServerTestCase):
    fixtures = ["testdata.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)
        cls.selenium.set_page_load_timeout(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
        

    def login(self):
        self.selenium.get(f"{self.live_server_url}/login")
        username_input = self.selenium.find_element(By.ID, "id_username")
        password_input = self.selenium.find_element(By.ID, "id_password")
        submit_btn = self.selenium.find_element(By.TAG_NAME, "button")
        username_input.send_keys("testuser")
        password_input.send_keys("testpassword")
        submit_btn.click()


    def logout(self):
        self.selenium.get(f"{self.live_server_url}/logout")


    def test_login_rendered(self):
        self.selenium.get(f"{self.live_server_url}/login")
        html = self.selenium.find_element(By.TAG_NAME, "html")
        self.assertIn("Welcome to Senψ", html.text)


    def test_chart_page_rendered(self):
        """
        Test objective:
        call statistics page should be rendered for a logged-in user
        """
        self.login()
        self.selenium.get(f"{self.live_server_url}/dataAnalysis?clientId=9")
        title = self.selenium.find_element(By.TAG_NAME, "h2")
        self.assertIsNotNone(title)
        self.assertIn("Data Analysis", title.text)
        self.logout()


    def test_no_data_no_chart(self):
        """
        Test objective:
        frontend should not render chart if data returned from API is empty
        """
        self.login()
        # test client with device_id='0e6b7ce2-633e-476a-9ca3-a19240faeca1'
        self.selenium.get(f"{self.live_server_url}/dataAnalysis?clientId=9")
        # select SMS tab
        smsTab = self.selenium.find_element(By.XPATH, '//a[@href="#smsTab"]')
        smsTab.click()

        chart = self.selenium.find_element(By.ID, "chart_sms_counts_trace")
        self.assertIsNotNone(chart)

        # click day, and select date range 01/01/2022 - 01/08/2022, which should return empty data
        
        select_day = self.selenium.find_element(By.XPATH, "//div[@id='sms_data_div']//input[@id='time-type-day']")
        start_date = self.selenium.find_element(By.XPATH, "//div[@id='sms_data_div']//input[@id='start-date']")
        end_date = self.selenium.find_element(By.XPATH, "//div[@id='sms_data_div']//input[@id='end-date']")
        submit = self.selenium.find_element(By.XPATH, "//div[@id='sms_data_div']//div[@id='sms_data_button']/button")

        select_day.click()
        start_date.clear()
        start_date.send_keys("01/01/2022")
        end_date.clear()
        end_date.send_keys("01/08/2022")
        self.assertEqual("01/01/2022", start_date.get_attribute("value"))
        self.assertEqual("01/08/2022", end_date.get_attribute("value"))
        submit.click()
        # accept the alert since no data returned
        alert = self.selenium.switch_to.alert
        alert.accept()

        # test if no chart rendered
        time.sleep(1)
        chart = self.selenium.find_element(By.ID, "chart_sms_counts_time")
        self.assertEqual(chart.rect["width"], 0)
        self.logout()
        

    def test_has_data_has_chart(self):
        """
        Test objective:
        frontend should rendered chart if data returned from API is not empty
        """
        self.login()
        # test client with device_id='0e6b7ce2-633e-476a-9ca3-a19240faeca1'
        self.selenium.get(f"{self.live_server_url}/dataAnalysis?clientId=9")

        # select SMS tab
        smsTab = self.selenium.find_element(By.XPATH, '//a[@href="#smsTab"]')
        smsTab.click()

        chart = self.selenium.find_element(By.ID, "chart_sms_counts_trace")
        self.assertIsNotNone(chart)

        # click day, and select date range 01/01/2022 - 01/08/2022, which should return empty data
        select_day = self.selenium.find_element(By.XPATH, "//div[@id='sms_data_div']//input[@id='time-type-day']")
        start_date = self.selenium.find_element(By.XPATH, "//div[@id='sms_data_div']//input[@id='start-date']")
        end_date = self.selenium.find_element(By.XPATH, "//div[@id='sms_data_div']//input[@id='end-date']")
        submit = self.selenium.find_element(By.XPATH, "//div[@id='sms_data_div']//div[@id='sms_data_button']/button")

        select_day.click()
        start_date.clear()
        start_date.send_keys("01/09/2022")
        end_date.clear()
        end_date.send_keys("01/18/2022")
        self.assertEqual("01/09/2022", start_date.get_attribute("value"))
        self.assertEqual("01/18/2022", end_date.get_attribute("value"))
        submit.click()

        # test if chart is rendered
        time.sleep(1)
        chart = self.selenium.find_element(By.ID, "chart_sms_counts_trace")
        self.assertGreater(chart.rect["width"], 0)
        self.logout()


    def test_delete_chart(self):
        """
        Test objective:
        After rendering a chart, user searched another time period which returned empty data,
        the chart should be deleted.
        """
        self.login()
        # test client with device_id='0e6b7ce2-633e-476a-9ca3-a19240faeca1'
        self.selenium.get(f"{self.live_server_url}/dataAnalysis?clientId=9")
        # select SMS tab
        smsTab = self.selenium.find_element(By.XPATH, '//a[@href="#smsTab"]')
        smsTab.click()

        chart = self.selenium.find_element(By.ID, "chart_sms_counts_trace")
        self.assertIsNotNone(chart)


        # click day, and select date range 01/01/2022 - 01/08/2022, which should return empty data
        select_day = self.selenium.find_element(By.XPATH, "//div[@id='sms_data_div']//input[@id='time-type-day']")
        start_date = self.selenium.find_element(By.XPATH, "//div[@id='sms_data_div']//input[@id='start-date']")
        end_date = self.selenium.find_element(By.XPATH, "//div[@id='sms_data_div']//input[@id='end-date']")
        submit = self.selenium.find_element(By.XPATH, "//div[@id='sms_data_div']//div[@id='sms_data_button']/button")

        select_day.click()
        start_date.clear()
        start_date.send_keys("01/09/2022")
        end_date.clear()
        end_date.send_keys("01/18/2022")
        self.assertEqual("01/09/2022", start_date.get_attribute("value"))
        self.assertEqual("01/18/2022", end_date.get_attribute("value"))
        submit.click()
        time.sleep(1)

        # test if chart is rendered
        chart = self.selenium.find_element(By.ID, "chart_sms_counts_trace")
        self.assertGreater(chart.rect["width"], 0)

        # now search the time period which cnotains no data
        select_day.click()
        start_date.clear()
        start_date.send_keys("01/01/2022")
        end_date.clear()
        end_date.send_keys("01/08/2022")
        self.assertEqual("01/01/2022", start_date.get_attribute("value"))
        self.assertEqual("01/08/2022", end_date.get_attribute("value"))
        submit.click()
        # accept the alert since no data returned
        alert = self.selenium.switch_to.alert
        alert.accept()

        # test if no chart rendered
        time.sleep(1)
        chart = self.selenium.find_element(By.ID, "chart_sms_counts_trace")
        self.assertEqual(chart.rect["width"], 0)

        self.logout()