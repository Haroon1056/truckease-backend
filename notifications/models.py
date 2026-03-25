from django.db import models
from django.conf import settings
from django.utils import timezone

class Notification(models.Model):
    """Push notification system"""
    
    NOTIFICATION_TYPES = [
        ('booking_created', 'New Booking Created'),
        ('booking_accepted', 'Booking Accepted'),
        ('booking_started', 'Trip Started'),
        ('booking_completed', 'Trip Completed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('booking_reminder', 'Booking Reminder'),
        ('payment_received', 'Payment Received'),
        ('vehicle_verified', 'Vehicle Verified'),
        ('vehicle_rejected', 'Vehicle Rejected'),
        ('review_received', 'New Review'),
        ('promotion', 'Promotion'),
        ('system', 'System Alert'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # Additional data
    data = models.JSONField(default=dict, help_text="Additional payload data")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # For FCM/APNS
    fcm_message_id = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    def mark_as_delivered(self):
        """Mark notification as delivered"""
        self.is_delivered = True
        self.delivered_at = timezone.now()
        self.save()

class UserDevice(models.Model):
    """User devices for push notifications"""
    
    DEVICE_TYPES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='devices'
    )
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES)
    device_token = models.CharField(max_length=500, unique=True)
    device_id = models.CharField(max_length=200, blank=True)
    
    # Device info
    app_version = models.CharField(max_length=20, blank=True)
    os_version = models.CharField(max_length=20, blank=True)
    model = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'device_token']
    
    def __str__(self):
        return f"{self.user.email} - {self.device_type} - {self.device_token[:20]}"