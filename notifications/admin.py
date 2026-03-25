from django.contrib import admin
from .models import Notification, UserDevice

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['user__email', 'title', 'message']
    readonly_fields = ['created_at', 'sent_at', 'read_at', 'delivered_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('Related Data', {
            'fields': ('booking', 'data')
        }),
        ('Status', {
            'fields': ('priority', 'is_read', 'read_at', 'is_sent', 'sent_at', 
                      'is_delivered', 'delivered_at', 'fcm_message_id')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )

@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_type', 'device_token', 'is_active', 'last_active']
    list_filter = ['device_type', 'is_active', 'created_at']
    search_fields = ['user__email', 'device_token']
    readonly_fields = ['created_at', 'last_active']