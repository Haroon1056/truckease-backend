from django.db import models
from django.conf import settings
from django.utils import timezone

class Vehicle(models.Model):
    """Vehicle model for driver trucks"""
    
    VEHICLE_TYPES = (
        ('small', 'Small Truck (Up to 2 tons)'),
        ('medium', 'Medium Truck (2-5 tons)'),
        ('large', 'Large Truck (5-10 tons)'),
        ('heavy', 'Heavy Truck (10+ tons)'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('inactive', 'Inactive'),
    )
    
    # Owner information
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vehicles',
        limit_choices_to={'user_type': 'driver'}
    )
    
    # Basic vehicle details
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    make = models.CharField(max_length=50)  # e.g., Toyota, Ford
    model = models.CharField(max_length=50)  # e.g., Hilux, F-150
    year = models.IntegerField()
    license_plate = models.CharField(max_length=20, unique=True)
    color = models.CharField(max_length=30, blank=True)
    
    # Capacity details
    capacity_tons = models.DecimalField(max_digits=5, decimal_places=2)
    dimensions = models.CharField(max_length=100, blank=True, help_text="Length x Width x Height")
    
    # Additional details
    description = models.TextField(blank=True)
    features = models.TextField(blank=True, help_text="AC, GPS, etc.")
    
    # Images
    front_image = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    back_image = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    side_image = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    interior_image = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    
    # Location
    current_city = models.CharField(max_length=100)
    current_area = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Status and verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verification_notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_vehicles',
        limit_choices_to={'user_type': 'admin'}
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Availability
    is_available = models.BooleanField(default=True)
    available_from = models.DateField(null=True, blank=True)
    available_to = models.DateField(null=True, blank=True)
    
    # Pricing
    base_price_per_km = models.DecimalField(max_digits=8, decimal_places=2)
    base_price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    waiting_charge_per_hour = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['driver', 'status']),
            models.Index(fields=['vehicle_type', 'status']),
            models.Index(fields=['license_plate']),
        ]
    
    def __str__(self):
        return f"{self.make} {self.model} - {self.license_plate} ({self.driver.email})"
    
    def verify(self, admin_user, notes=""):
        """Verify vehicle"""
        self.status = 'verified'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.verification_notes = notes
        self.save()
    
    def reject(self, admin_user, notes=""):
        """Reject vehicle"""
        self.status = 'rejected'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.verification_notes = notes
        self.save()
    
    @property
    def is_verified(self):
        return self.status == 'verified'
    
    @property
    def full_name(self):
        return f"{self.make} {self.model} ({self.year})"