from django.test import TestCase, Client
from django.urls import reverse
from datetime import datetime, timedelta
from django.contrib.auth.models import User, Permission
from home.models import Calls  # 如果需要使用模型
from home.models import Client as ct
from model_mommy import mommy

class CallsViewsTest(TestCase):
    def setUp(self):
        timestamps = [
            datetime(2023, 1, 1),
            datetime(2023, 1, 2),
            datetime(2023, 1, 3),
            datetime(2023, 1, 4),
            datetime(2023, 1, 5),
        ]
        mommy.make(ct, client_id=1, client_device_id="test1")
        mommy.make(ct, client_id=2, client_device_id=None)
        mommy.make(ct, client_id=3, client_device_id="test2")
        client_instance = ct.objects.get(client_device_id="test1")
        for timestamp in timestamps:
            timestamp_ms = int(timestamp.timestamp() * 1000)
            mommy.make(Calls, device_id=client_instance, timestamp=timestamp_ms)
        self.client = Client()
        self.client_id = 1
        self.start_time = "2023-01-01"
        self.end_time = "2023-01-14"
        self.user = User.objects.create_user(username='@test1', password='testpassword1')
        calls_permission = Permission.objects.get(codename='view_calls')
        sms_permission = Permission.objects.get(codename='view_messages')
        self.user.user_permissions.add(calls_permission)
        self.user.user_permissions.add(sms_permission)
        self.client.login(username='@test1', password='testpassword1')

    def test_get_call_duration_time1(self):#valid time, timetype=0
        url = reverse('call_duration_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'time_type': '0'  # 假设测试日时间类型
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)

    def test_get_call_duration_time2(self):  # Invalid time
        url = reverse('call_duration_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-16",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid time range', data["error_message"])

    def test_get_call_duration_time3(self):  # Invalid time
        url = reverse('call_duration_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-02",
            'end_time': "2023-01-01",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid time range', data["error_message"])

    def test_get_call_duration_time4(self):#valid time, timetype=1
        url = reverse('call_duration_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-12-01",
            'time_type': '1'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)

    def test_get_call_duration_time5(self):#valid time, timetype=2
        url = reverse('call_duration_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2024-12-01",
            'time_type': '2'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)

    def test_get_call_duration_time6(self):#valid time, invalid timetype
        url = reverse('call_duration_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2024-12-01",
            'time_type': '3'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid timetype', data["error_message"])

    def test_get_call_duration_time7(self):  # No client
        url = reverse('call_duration_time', args=[10])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('No Client', data["error_message"])

    def test_get_call_duration_time8(self):  # Client Doesn't Have Device Id
        url = reverse('call_duration_time', args=[2])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual("Client Doesn't Have Device Id", data['error_message'])

    def test_get_call_duration_time9(self):  # Client Doesn't Have record
        url = reverse('call_duration_time', args=[3])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual({'record': []}, data)

    def test_get_call_duration_time10(self):  # no end_time
        url = reverse('call_duration_time', args=[1])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid time range', data["error_message"])

    def test_get_call_duration_time11(self):  # time_type = 1, invalid time
        url = reverse('call_duration_time', args=[1])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2048-01-10",
            'time_type': '1'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid time range', data["error_message"])
    def test_get_call_duration_time12(self):  # time_type = 2, invalid time
        url = reverse('call_duration_time', args=[1])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2048-01-10",
            'time_type': '2'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid time range', data["error_message"])

    def test_get_call_counts_time1(self):  # valid time, timetype=0
        url = reverse('call_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'time_type': '0'  # 假设测试日时间类型
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()  # 检查响应中的数据是否符合预期
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)

    def test_get_call_counts_time2(self):  # Invalid time
        url = reverse('call_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-16",
            'time_type': '0'  # 假设测试日时间类型
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()  # 检查响应中的数据是否符合预期
        self.assertIn('error_message', data)
        self.assertEqual('Invalid time range', data["error_message"])

    def test_get_call_counts_time3(self):  # Invalid time
        url = reverse('call_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-02",
            'end_time': "2023-01-01",
            'time_type': '0'  # 假设测试日时间类型
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()  # 检查响应中的数据是否符合预期
        self.assertIn('error_message', data)
        self.assertEqual('Invalid time range', data["error_message"])

    def test_get_call_counts_time4(self):#valid time, timetype=1
        url = reverse('call_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-12-01",
            'time_type': '1'  # 假设测试日时间类型
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()# 检查响应中的数据是否符合预期
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)

    def test_get_call_counts_time5(self):#valid time, timetype=2
        url = reverse('call_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2024-12-01",
            'time_type': '2'  # 假设测试日时间类型
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()# 检查响应中的数据是否符合预期
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)

    def test_get_call_counts_time6(self):#valid time, invalid timetype
        url = reverse('call_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2024-12-01",
            'time_type': '3'  # 假设测试日时间类型
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()  # 检查响应中的数据是否符合预期
        self.assertIn('error_message', data)
        self.assertEqual('Invalid timetype', data["error_message"])

    def test_get_call_counts_time7(self):  # No client
        url = reverse('call_counts_time', args=[10])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('No Client', data["error_message"])

    def test_get_call_counts_time8(self):#Client Doesn't Have Device Id'
        url = reverse('call_counts_time', args=[2])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual("Client Doesn't Have Device Id", data['error_message'])

    def test_get_call_counts_time9(self):  # Client Doesn't Have record
        url = reverse('call_counts_time', args=[3])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual({'record': []}, data)

    def test_get_call_counts_time10(self):  # time_type = 1, invalid time
        url = reverse('call_counts_time', args=[1])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2048-01-10",
            'time_type': '1'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid time range', data["error_message"])
    def test_get_call_counts_time11(self):  # time_type = 2, invalid time
        url = reverse('call_counts_time', args=[1])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2048-01-10",
            'time_type': '2'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid time range', data["error_message"])

    def test_get_call_duration_trace1(self):  # valid time
        url = reverse('call_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()  # 检查响应中的数据是否符合预期
        self.assertIn('record', data)
        self.assertLessEqual(len(data['record']), 10)
        self.assertIsInstance(data['record'], list)

    def test_get_call_duration_trace2(self):#call type =1
        url = reverse('call_duration_trace', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'call_type': '1',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)
        self.assertLessEqual(len(data['record']), 10)

    def test_get_call_duration_trace3(self):#invalid call type =3
        url = reverse('call_duration_trace', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'call_type': '3',
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid call type', data["error_message"])

    def test_get_call_duration_trace4(self):  # No client
        url = reverse('call_duration_trace', args=[10])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('No Client', data["error_message"])

    def test_get_call_duration_trace5(self):#Client Doesn't Have Device Id'
        url = reverse('call_duration_trace', args=[2])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual("Client Doesn't Have Device Id", data['error_message'])

    def test_get_call_duration_trace6(self):  # Client Doesn't Have record
        url = reverse('call_duration_trace', args=[3])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual({'record': []}, data)

    def test_get_call_counts_trace1(self):  # valid time
        url = reverse('call_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('record', data)
        self.assertLessEqual(len(data['record']), 10)
        self.assertIsInstance(data['record'], list)

    def test_get_call_counts_trace2(self):  # call type =1
        url = reverse('call_duration_trace', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'call_type': '1',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)
        self.assertLessEqual(len(data['record']), 10)

    def test_get_call_counts_trace3(self):#invalid call type =3
        url = reverse('call_duration_trace', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'call_type': '3',
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid call type', data["error_message"])

    def test_get_call_counts_trace4(self):  # No client
        url = reverse('call_counts_trace', args=[10])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('No Client', data["error_message"])

    def test_get_call_counts_trace5(self):#Client Doesn't Have Device Id'
        url = reverse('call_counts_trace', args=[2])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual("Client Doesn't Have Device Id", data['error_message'])

    def test_get_call_counts_trace6(self):  # Client Doesn't Have record
        url = reverse('call_counts_trace', args=[3])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual({'record': []}, data)

    def test_get_call_counts_trace7(self):#call type =3
        url = reverse('call_counts_trace', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'call_type': '3',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)
        self.assertLessEqual(len(data['record']), 10)


    def test_get_call_counts_trace8(self):  # call type =2
        url = reverse('call_duration_trace', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'call_type': '2',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)
        self.assertLessEqual(len(data['record']), 10)
    def test_get_call_counts_trace9(self):  # invalid call type =4
        url = reverse('call_counts_trace', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'call_type': '4',
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid call type', data["error_message"])

# test messages
    def test_get_sms_counts_time1(self):  # valid time, timetype=0
        url = reverse('sms_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)

    def test_get_sms_counts_time2(self):  # Invalid time
        url = reverse('sms_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-16",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid time range', data["error_message"])

    def test_get_sms_counts_time3(self):  # Invalid time
        url = reverse('sms_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-02",
            'end_time': "2023-01-01",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid time range', data["error_message"])

    def test_get_sms_counts_time4(self):#valid time, timetype=1
        url = reverse('sms_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-12-01",
            'time_type': '1'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)

    def test_get_sms_counts_time5(self):#valid time, timetype=2
        url = reverse('sms_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2024-12-01",
            'time_type': '2'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)

    def test_get_sms_counts_time6(self):#valid time, invalid timetype
        url = reverse('sms_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2024-12-01",
            'time_type': '3'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid timetype', data["error_message"])

    def test_get_sms_counts_time7(self):  # No client
        url = reverse('sms_counts_time', args=[10])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('No Client', data["error_message"])

    def test_get_sms_counts_time8(self):#Client Doesn't Have Device Id'
        url = reverse('sms_counts_time', args=[2])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual("Client Doesn't Have Device Id", data['error_message'])

    def test_get_sms_counts_time9(self):  # Client Doesn't Have record
        url = reverse('sms_counts_time', args=[3])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
            'time_type': '0'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual({'record': []}, data)

    def test_get_sms_counts_time10(self):  # Invalid time
        url = reverse('sms_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2048-01-16",
            'time_type': '1'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid time range', data["error_message"])

    def test_get_sms_counts_time11(self):  # Invalid time
        url = reverse('sms_counts_time', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2048-01-16",
            'time_type': '2'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid time range', data["error_message"])

    def test_get_sms_counts_trace1(self):  # valid time, timetype=0
        url = reverse('sms_counts_trace', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('record', data)
        self.assertLessEqual(len(data['record']), 10)
        self.assertIsInstance(data['record'], list)

    def test_get_sms_counts_trace2(self):  # sms type =1
        url = reverse('sms_counts_trace', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'message_type': '1',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('record', data)
        self.assertIsInstance(data['record'], list)
        self.assertLessEqual(len(data['record']), 10)

    def test_get_sms_counts_trace3(self):#invalid sms type =3
        url = reverse('sms_counts_trace', args=[self.client_id])
        response = self.client.get(url, {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'message_type': '3',
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('Invalid message type', data["error_message"])

    def test_get_sms_counts_trace4(self):  # No client
        url = reverse('sms_counts_trace', args=[10])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
            'message_type': '1',
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual('No Client', data["error_message"])

    def test_get_sms_counts_trace5(self):#Client Doesn't Have Device Id'
        url = reverse('sms_counts_trace', args=[2])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
            'message_type': '1',
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error_message', data)
        self.assertEqual("Client Doesn't Have Device Id", data['error_message'])

    def test_get_sms_counts_trace6(self):  # Client Doesn't Have record
        url = reverse('sms_counts_trace', args=[3])
        response = self.client.get(url, {
            'start_time': "2023-01-01",
            'end_time': "2023-01-10",
            'message_type': '1',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual({'record': []}, data)