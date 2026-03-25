from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class Booking(models.Model):
    """Booking model for truck reservations"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected by Driver'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('partial', 'Partial Paid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    )
    
    # Relationships
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings_as_customer',
        limit_choices_to={'user_type': 'customer'}
    )
    
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings_as_driver',
        limit_choices_to={'user_type': 'driver'}
    )
    
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )
    
    # Trip details
    pickup_address = models.TextField()
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    dropoff_address = models.TextField()
    dropoff_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    dropoff_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Cargo details
    cargo_type = models.CharField(max_length=100)
    cargo_weight = models.DecimalField(max_digits=8, decimal_places=2, help_text="Weight in tons")
    cargo_description = models.TextField(blank=True)
    is_hazardous = models.BooleanField(default=False)
    
    # Schedule
    pickup_time = models.DateTimeField()
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    actual_pickup_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)
    
    # Pricing
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    distance_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    waiting_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, default='cash')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cancellation_reason = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_bookings'
    )
    
    # Additional notes
    customer_notes = models.TextField(blank=True)
    driver_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['driver', 'status']),
            models.Index(fields=['pickup_time']),
            models.Index(fields=['status', 'payment_status']),
        ]
    
    def __str__(self):
        return f"Booking #{self.id} - {self.customer.email} - {self.status}"
    
    def calculate_total(self):
        """Calculate total amount based on distance and waiting time"""
        total = self.base_fare + self.distance_charge + self.waiting_charge
        return total
    
    def accept_booking(self, driver, vehicle):
        """Accept booking by driver"""
        self.status = 'accepted'
        self.driver = driver
        self.vehicle = vehicle
        self.save()
    
    def start_trip(self):
        """Start the trip"""
        self.status = 'in_progress'
        self.actual_pickup_time = timezone.now()
        self.save()
    
    def complete_trip(self):
        """Complete the trip"""
        self.status = 'completed'
        self.actual_delivery_time = timezone.now()
        self.save()
    
    def cancel_booking(self, user, reason=""):
        """Cancel the booking"""
        self.status = 'cancelled'
        self.cancelled_by = user
        self.cancellation_reason = reason
        self.save()
    
    def reject_booking(self, reason=""):
        """Driver rejects booking"""
        self.status = 'rejected'
        self.driver_notes = reason
        self.save()

class BookingHistory(models.Model):
    """Track booking status changes"""
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.booking} - {self.status} at {self.created_at}"