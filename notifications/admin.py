from django.contrib import admin
from .models import Notification, UserDevice


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Notification Admin
    Manage push notifications sent to users
    """
    
    list_display = (
        'id',
        'user',
        'title',
        'notification_type',
        'is_read',
        'priority',
        'created_at'
    )
    
    list_filter = (
        'notification_type',
        'is_read',
        'priority',
        'created_at'
    )
    
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at', 'read_at', 'sent_at', 'delivered_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Notification Details', {
            'fields': ('notification_type', 'title', 'message')
        }),
        ('Related Data', {
            'fields': ('booking', 'data')
        }),
        ('Priority & Status', {
            'fields': (
                'priority',
                'is_read', 'read_at',
                'is_sent', 'sent_at',
                'is_delivered', 'delivered_at'
            )
        }),
        ('FCM', {
            'fields': ('fcm_message_id',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read"""
        for notification in queryset:
            notification.mark_as_read()
        self.message_user(request, f"{queryset.count()} notification(s) marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread"""
        queryset.update(is_read=False, read_at=None)
        self.message_user(request, f"{queryset.count()} notification(s) marked as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    """
    User Device Admin
    Manage devices registered for push notifications
    """
    
    list_display = (
        'id',
        'user',
        'device_type',
        'device_token',
        'is_active',
        'last_active'
    )
    
    list_filter = ('device_type', 'is_active')
    search_fields = ('user__email', 'device_token')
    readonly_fields = ('created_at', 'last_active')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Device Information', {
            'fields': ('device_type', 'device_token', 'device_id')
        }),
        ('Device Details', {
            'fields': ('app_version', 'os_version', 'model')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_active')
        }),
    )