from django.contrib import admin
from .models import Notification, UserDevice

# Simplified Notification Admin
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__email', 'title')
    readonly_fields = ('created_at',)

# Simplified UserDevice Admin
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'device_type', 'device_token', 'is_active')
    list_filter = ('device_type', 'is_active')
    search_fields = ('user__email', 'device_token')

admin.site.register(Notification, NotificationAdmin)
admin.site.register(UserDevice, UserDeviceAdmin)