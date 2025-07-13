from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    client_name = models.CharField(max_length=255)
    client_password = models.CharField(max_length=255)
    client_gender = models.CharField(max_length=255)
    client_birthday = models.DateField()
    client_title = models.CharField(max_length=255)
    client_first_name = models.CharField(max_length=255)
    client_last_name = models.CharField(max_length=255)
    client_facebook_id = models.CharField(max_length=255)
    client_twitter_id = models.CharField(max_length=255)
    client_device_id = models.CharField(max_length=150, unique=True, null=True)
    clinician_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, to_field='id', db_column='clinician_id')
    class Meta:
        db_table = 'client'


class Calls(models.Model):
    _id = models.AutoField(primary_key=True)
    call_type = models.IntegerField()
    call_duration = models.IntegerField()
    # device_id = models.ForeignKey(Client, on_delete=models.CASCADE, to_field='client_device_id', db_column='device_id')
    device_id = models.CharField(max_length=150)
    timestamp = models.FloatField()
    trace = models.TextField()
    class Meta:
        db_table = 'calls'


class Messages(models.Model):
    _id = models.AutoField(primary_key=True)
    timestamp = models.FloatField()
    # device_id = models.ForeignKey(Client, on_delete=models.CASCADE, to_field='client_device_id', db_column='device_id')
    device_id = models.CharField(max_length=150)
    message_type = models.IntegerField()
    trace = models.TextField()

    class Meta:
        db_table = "messages"

# class Aware_device(models.Model):
#     _id = models.AutoField(primary_key=True)
#     timestamp = models.FloatField()
#     # device_id = models.ForeignKey(Client, on_delete=models.CASCADE, to_field='client_device_id', db_column='device_id')
#     board = models.TextField()
#     brand = models.TextField()
#     device = models.TextField()
#     build_id = models.TextField()
#     hardware = models.TextField()
#     manufacturer = models.TextField()
#     model = models.TextField()
#     product = models.TextField()
#     serial = models.TextField()
#     release = models.TextField()
#     release_type = models.TextField()
#     sdk = models.TextField()
#     label = models.TextField()
#
#     class Meta:
#         db_table = "aware_device"

