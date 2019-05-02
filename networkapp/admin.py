from django.contrib import admin
from networkapp.models import UserProfileInfo,DeviceCredentialDetail,DeviceCommandInfo,CollectionInfo
# Register your models here.
admin.site.register(UserProfileInfo)
admin.site.register(DeviceCredentialDetail)
admin.site.register(DeviceCommandInfo)
admin.site.register(CollectionInfo)

