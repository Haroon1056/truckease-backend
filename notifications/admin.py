from django.contrib import admin
from .models import Notification, UserDevice

class NotificationAdmin(admin.ModelAdmin):
    pass

class UserDeviceAdmin(admin.ModelAdmin):
    pass

admin.site.register(Notification, NotificationAdmin)
admin.site.register(UserDevice, UserDeviceAdmin)