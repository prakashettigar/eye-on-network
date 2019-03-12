from django import forms
from django.contrib.auth.models import User
from networkapp.models import UserProfileInfo
from networkapp.models import DeviceCredentialDetail,DeviceCommandInfo

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta():
        model = User
        fields = ('username','email','password')

class UserProfileInfoForm(forms.ModelForm):
    full_name = forms.CharField(required=True)
    class Meta():
        model = UserProfileInfo
        fields = ('full_name','profile_pic')

class DeviceCredentialForm(forms.ModelForm):
    device_password = forms.CharField(widget=forms.PasswordInput())
    device_ip = forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control' , 'autocomplete': 'off','pattern':'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', 'title':'Enter IP Address ','onblur':'ipvalidation(this.value);'}))
    device_username = forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control' , 'autocomplete': 'off', 'title':'Enter Username'}))
    class Meta():
        model = DeviceCredentialDetail
        fields =('device_ip','device_username','device_password')

class DeviceCommandForm(forms.ModelForm):
    class Meta():
        model = DeviceCommandInfo
        fields = ('device_command','command_name')