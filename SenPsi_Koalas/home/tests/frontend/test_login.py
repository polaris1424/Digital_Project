from django.test import TestCase
from django.urls import reverse

# run python manage.py tests home.tests.front-end.login_test


class LoginTest(TestCase):
    def test_template_contains_login_text(self):
        response = self.client.get(
            reverse('view_login'))
        self.assertContains(response, 'Sign in', status_code=200)
