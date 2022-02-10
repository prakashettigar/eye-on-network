from django.conf.urls import re_path
from networkapp import views

app_name = 'networkapp'

urlpatterns = [
    re_path(r'dashboard/$',views.dashboard,name='dashboard'),
    re_path(r'register/$',views.register,name='register'),
    re_path(r'user_login/$',views.user_login,name='user_login'),
    re_path(r'device_discovery/$',views.device_discovery,name='device_discovery'),
    re_path(r'adddevice_credential/$',views.add_device_credential,name='add_device_credential'),
    re_path(r'add_device_commands/$',views.add_device_commands,name='add_device_commands'),
    re_path(r'fetch_device_configuration/$',views.fetch_device_configuration,name='fetch_device_configuration'),
    re_path(r'device_configuration/$',views.device_configuration,name='device_configuration'),
    re_path(r'getDashboardDetails/$',views.getDashboardDetails,name='getDashboardDetails'),
    re_path(r'device_access/$',views.device_access,name='device_access')
]
