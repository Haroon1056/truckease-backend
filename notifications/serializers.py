from rest_framework import serializers
from .models import Notification, UserDevice

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_name', 'notification_type', 'title', 'message',
            'booking', 'data', 'priority', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user']

class NotificationMarkReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read"""
    
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    mark_all = serializers.BooleanField(default=False)

class UserDeviceSerializer(serializers.ModelSerializer):
    """Serializer for user devices"""
    
    class Meta:
        model = UserDevice
        fields = [
            'id', 'device_type', 'device_token', 'device_id',
            'app_version', 'os_version', 'model', 'is_active',
            'created_at', 'last_active'
        ]
        read_only_fields = ['id', 'created_at', 'last_active']

class NotificationCountSerializer(serializers.Serializer):
    """Serializer for notification count"""
    
    unread_count = serializers.IntegerField()
    total_count = serializers.IntegerField()