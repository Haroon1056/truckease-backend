from django.db import models
from django.conf import settings
from django.utils import timezone

class LocationUpdate(models.Model):
    """Real-time location updates for vehicles - Simplified version"""
    
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.CASCADE,
        related_name='location_updates',
        null=True,
        blank=True
    )
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='location_updates'
    )
    
    # Location data (using decimal fields instead of GIS)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    heading = models.IntegerField(null=True, blank=True, help_text="Direction in degrees")
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['vehicle', '-timestamp']),
            models.Index(fields=['booking', '-timestamp']),
        ]
    
    def __str__(self):
        return f"Location for {self.vehicle or self.booking} at ({self.latitude}, {self.longitude})"

class TripRoute(models.Model):
    """Pre-calculated route for a trip"""
    
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='route')
    
    # Route details
    origin_lat = models.DecimalField(max_digits=9, decimal_places=6)
    origin_lng = models.DecimalField(max_digits=9, decimal_places=6)
    destination_lat = models.DecimalField(max_digits=9, decimal_places=6)
    destination_lng = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Route data
    route_points = models.JSONField(default=list, help_text="List of lat/lng points")
    distance_meters = models.IntegerField()
    duration_seconds = models.IntegerField()
    polyline = models.TextField(blank=True, help_text="Encoded polyline for map display")
    
    # Traffic and ETA updates
    current_eta = models.DateTimeField(null=True, blank=True)
    traffic_delay_minutes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['booking']),
        ]
    
    def __str__(self):
        return f"Route for Booking #{self.booking.id}"