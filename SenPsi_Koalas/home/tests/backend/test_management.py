from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission
import json
from django.contrib.auth import authenticate, login, logout
from django.test.client import RequestFactory
from home.views import add_client
from home.models import Client as ct
from model_mommy import mommy
from datetime import datetime
class ManagementViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='@test1', password='testpassword1')
        # self.user = User.objects.create_user(username='@test1', password='testpassword1')
        calls_permission = Permission.objects.get(codename='view_calls')
        sms_permission = Permission.objects.get(codename='view_messages')
        self.user.user_permissions.add(calls_permission)
        self.user.user_permissions.add(sms_permission)
        self.login_url = reverse('view_login')

        mommy.make(ct, clinician_id=self.user, client_id=1, client_name="aa", client_gender="male")
    def test_login1(self):#valid user
        response = self.client.post(self.login_url, {'username': '@test1', 'password': 'testpassword1'})
        self.assertRedirects(response, '/homePage')
        self.assertEqual(response.status_code, 302)

    def test_login2(self):#valid admin user
        permission = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(permission)
        response = self.client.post(self.login_url, {'username': '@test1', 'password': 'testpassword1'})
        self.assertRedirects(response, '/admin/auth/user/', target_status_code=302)
        self.assertEqual(response.status_code, 302)

    def test_login3(self):# invalid user
        response = self.client.post(self.login_url, {'username': 'invaliduser', 'password': 'invalidpassword'})
        self.assertEqual(response.status_code, 200)
        form_error = response.context['form'].non_field_errors()
        self.assertEqual(form_error[0], "Please enter a correct username and password. Note that both fields may be case-sensitive.")

    def test_login4(self):#invalid form
        response = self.client.post(self.login_url, {})
        form = response.context['form']
        username_errors = form['username'].errors
        password_errors = form['password'].errors
        self.assertEqual(username_errors[0], "This field is required.")
        self.assertEqual(password_errors[0], "This field is required.")
    def test_login5(self):#incorrect password
        response = self.client.post(self.login_url, {'username': '@test1', 'password': 'invalidpassword1'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'views/Login/index.html')
        form_error = response.context['form'].non_field_errors()
        print(form_error)
        self.assertEqual(form_error[0], "Please enter a correct username and password. Note that both fields may be case-sensitive.")

    def test_logout1(self):
        self.client.login(username='@test1', password='testpassword1')
        response = self.client.get(reverse('view_logout'))
        self.assertRedirects(response, reverse('view_login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout2(self):
        response = self.client.get(reverse('view_logout'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_add_client1(self):
        permission = Permission.objects.get(codename='add_client')
        self.user.user_permissions.add(permission)
        user_id = self.user.id
        self.client.login(username='@test1', password='testpassword1')
        url = reverse('add_client', args=[user_id])
        data = {
            'client_name': 'John Doe',
            'client_gender': 'Male',
            'client_birthday': '1990-01-01',
            'client_title': 'Mr',
            'client_first_name': 'John',
            'client_last_name': 'Doe',
            'client_facebook_id': 'john.doe.facebook',
            'client_twitter_id': 'john_doe_twitter',
            'client_device_id': '123456'
        }
        response = self.client.post(url, data)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Client added successfully')
        self.assertEqual(response.status_code, 200)
        client_exists = ct.objects.filter(client_name="John Doe").exists()
        self.assertTrue(client_exists)

    def test_add_client2(self):
        permission = Permission.objects.get(codename='add_client')
        self.user.user_permissions.add(permission)
        user_id = self.user.id
        self.client.login(username='@test1', password='testpassword1')
        url = reverse('add_client', args=[user_id])
        data = {
            'client_title': 'Mr',
            'client_first_name': 'John',
            'client_last_name': 'Doe',
            'client_facebook_id': 'john.doe.facebook',
            'client_twitter_id': 'john_doe_twitter',
            'client_device_id': '123456'
        }
        response = self.client.post(url, data)
        response_data = json.loads(response.content)
        self.assertIn('error_message', response_data)
        self.assertEqual(response.status_code, 400)

    def test_delete_client1(self):
        permission = Permission.objects.get(codename='add_client')
        permission2 = Permission.objects.get(codename='delete_client')
        self.user.user_permissions.add(permission, permission2)
        self.client.login(username='@test1', password='testpassword1')
        url = reverse('delete_client', args=[1])#1 because:mummy create 1 test in user table，1 login，1 create succsss before，this is 3
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['message'], 'Client deleted successfully')
        client_exists = ct.objects.filter(client_name="aa").exists()
        self.assertFalse(client_exists, "Client should be deleted")

    def test_delete_client2(self):
        permission = Permission.objects.get(codename='add_client')
        permission2 = Permission.objects.get(codename='delete_client')
        self.user.user_permissions.add(permission, permission2)
        # user_id = self.user.id
        self.client.login(username='@test1', password='testpassword1')
        url = reverse('delete_client', args=[9])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error_message', response_data)
        client_exists = ct.objects.filter(client_name="aa").exists()
        self.assertTrue(client_exists)

    def test_get_all_clients1(self):
        permission = Permission.objects.get(codename='add_client')
        permission2 = Permission.objects.get(codename='view_client')
        self.user.user_permissions.add(permission, permission2)
        self.client.login(username='@test1', password='testpassword1')
        url = reverse('get_all_clients', args=[self.user.id])
        page = 1
        response = self.client.get(url,{'page': page})
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["client_list"][0]["client_name"],"aa")
        self.assertIn('client_list', response_data)
        self.assertIn('total_pages', response_data)

    def test_get_all_clients2(self):
        permission = Permission.objects.get(codename='add_client')
        permission2 = Permission.objects.get(codename='view_client')
        self.user.user_permissions.add(permission, permission2)
        self.client.login(username='@test1', password='testpassword1')
        url = reverse('get_all_clients', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["client_list"][0]["client_name"],"aa")
        self.assertIn('client_list', response_data)
        self.assertIn('total_pages', response_data)
    def test_get_all_clients3(self):#page invalid will call page empty
        permission = Permission.objects.get(codename='add_client')
        permission2 = Permission.objects.get(codename='view_client')
        self.user.user_permissions.add(permission, permission2)
        self.client.login(username='@test1', password='testpassword1')
        url = reverse('get_all_clients', args=[self.user.id])
        page = 1000
        response = self.client.get(url,{'page': page})
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["client_list"][0]["client_name"],"aa")
        self.assertIn('client_list', response_data)
        self.assertIn('total_pages', response_data)


    def test_get_client_by_id1(self):#
        permission = Permission.objects.get(codename='view_client')
        self.user.user_permissions.add(permission)
        self.client.login(username='@test1', password='testpassword1')
        client_id = 1
        url = reverse('get_client_by_id', args=[client_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual("aa", response_data[0]["client_name"])

    def test_get_client_by_id2(self):#
        permission = Permission.objects.get(codename='view_client')
        self.user.user_permissions.add(permission)
        self.client.login(username='@test1', password='testpassword1')
        client_id = 3
        url = reverse('get_client_by_id', args=[client_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual([], response_data)

    def test_get_client_by_name1(self):#
        permission = Permission.objects.get(codename='view_client')
        self.user.user_permissions.add(permission)
        self.client.login(username='@test1', password='testpassword1')
        client_name = "aa"
        url = reverse('get_client_by_name', args=[self.user.id, client_name])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual("aa", response_data[0]["client_name"])
        self.assertEqual(1, response_data[0]["client_id"])

    def test_get_client_by_name2(self):#
        permission = Permission.objects.get(codename='view_client')
        self.user.user_permissions.add(permission)
        self.client.login(username='@test1', password='testpassword1')
        client_name = "xxx"
        url = reverse('get_client_by_name', args=[self.user.id, client_name])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual([], response_data)

    def test_update_client1(self):
        permission = Permission.objects.get(codename='change_client')
        self.user.user_permissions.add(permission)
        user_id = self.user.id
        self.client.login(username='@test1', password='testpassword1')
        client_id = 1
        url = reverse('update_client', args=[client_id])  # 请替换成实际的 URL 别名和 clinician_id
        data = {
            'client_gender': 'Female',
            'client_birthday': '1990-01-01',
            'client_title': 'Mr',
            'client_first_name': 'John',
            'client_last_name': 'Doe',
            'client_facebook_id': 'john.doe.facebook',
            'client_twitter_id': 'john_doe_twitter',
            'client_device_id': '123456'
        }
        response = self.client.post(url, data)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Client updated successfully')
        self.assertEqual(response.status_code, 200)
        client_exists = ct.objects.filter(
            client_gender="Female",
            client_title='Mr',
            client_first_name='John',
            client_last_name='Doe',
            client_facebook_id='john.doe.facebook',
            client_twitter_id='john_doe_twitter',
            client_device_id='123456'
        ).exists()
        self.assertTrue(client_exists)

    def test_update_client2(self):#update name will be wrong
        permission = Permission.objects.get(codename='change_client')
        self.user.user_permissions.add(permission)
        user_id = self.user.id
        self.client.login(username='@test1', password='testpassword1')
        client_id = 1
        url = reverse('update_client', args=[client_id])
        data = {
            'client_name': "JJ",
            'client_gender': 'Female',
            'client_birthday': '1990-01-01',
            'client_title': 'Mr',
            'client_first_name': 'John',
            'client_last_name': 'Doe',
            'client_facebook_id': 'john.doe.facebook',
            'client_twitter_id': 'john_doe_twitter',
            'client_device_id': '123456'
        }
        response = self.client.post(url, data)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Client updated successfully')
        self.assertEqual(response.status_code, 200)
        client_exists = ct.objects.filter(
            client_name= "JJ",
            client_gender="Female",
            client_title='Mr',
            client_first_name='John',
            client_last_name='Doe',
            client_facebook_id='john.doe.facebook',
            client_twitter_id='john_doe_twitter',
            client_device_id='123456'
        ).exists()
        self.assertFalse(client_exists)

    def test_update_client3(self):  # update wrong
        permission = Permission.objects.get(codename='change_client')
        self.user.user_permissions.add(permission)
        user_id = self.user.id
        self.client.login(username='@test1', password='testpassword1')
        client_id = 3
        url = reverse('update_client', args=[client_id])
        data = {
            'client_gender2': 'Female',
        }
        response = self.client.post(url, data)
        response_data = json.loads(response.content)
        self.assertIn('error_message', response_data)
        self.assertEqual(response.status_code, 400)

    def test_route1(self):
        self.client.login(username='@test1', password='testpassword1')
        response = self.client.get(reverse('dataAnalysis'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'views/dataAnalysis/index.html')

        response = self.client.get(reverse('homePage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'views/homePage/index.html')

        response = self.client.get(reverse('viewClient'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'views/viewClient/index.html')

        response = self.client.get(reverse('addClient'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'views/addClient/index.html')

        response = self.client.get(reverse('call_data'))
        self.assertTemplateUsed(response, 'views/dataAnalysis/call_data.html')

        response = self.client.get(reverse('sms_data'))
        self.assertTemplateUsed(response, 'views/dataAnalysis/sms_data.html')


    def test_route2(self):
        response = self.client.get(reverse('homePage'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('view_login'))

        response = self.client.get(reverse('viewClient'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('view_login'))

        response = self.client.get(reverse('addClient'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('view_login'))

        response = self.client.get(reverse('dataAnalysis'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('view_login'))



