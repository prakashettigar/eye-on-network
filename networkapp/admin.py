from django.contrib import admin
from networkapp.models import UserProfileInfo,DeviceCredentialDetail,DeviceCommandInfo
# Register your models here.
admin.site.register(UserProfileInfo)
admin.site.register(DeviceCredentialDetail)
admin.site.register(DeviceCommandInfo)

