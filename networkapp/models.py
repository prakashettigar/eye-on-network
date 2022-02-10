from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
# Create your models here.

class UserProfileInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    profile_pic = models.ImageField(upload_to='profile_pics',blank=True)

class DeviceCredentialDetail(models.Model):
    device_ip = models.CharField(max_length=15,unique=True)
    device_username = models.CharField(max_length=50)
    device_password = models.CharField(max_length=50)

class DeviceCommandInfo(models.Model):
    device_command =models.CharField(max_length=100,unique=True)
    command_name = models.CharField(max_length=30,unique=True)

class CollectionInfo(models.Model):
    auto_increment_id = models.AutoField(primary_key=True)
    filepath = models.CharField(max_length=100,unique=True)
    created_on = models.DateTimeField(auto_now=True)
