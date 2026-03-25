from django.contrib import admin
from .models import LocationUpdate, TripRoute

@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'booking', 'latitude', 'longitude', 'speed', 'timestamp']
    list_filter = ['is_active', 'timestamp']
    search_fields = ['vehicle__license_plate', 'booking__id']
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Location', {'fields': ('latitude', 'longitude', 'speed', 'heading', 'accuracy')}),
        ('Related', {'fields': ('vehicle', 'booking')}),
        ('Status', {'fields': ('is_active', 'timestamp')}),
    )

@admin.register(TripRoute)
class TripRouteAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'distance_meters', 'duration_seconds', 'traffic_delay_minutes', 'created_at']
    search_fields = ['booking__id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Booking', {'fields': ('booking',)}),
        ('Route Details', {'fields': ('origin_lat', 'origin_lng', 'destination_lat', 'destination_lng')}),
        ('Route Data', {'fields': ('route_points', 'distance_meters', 'duration_seconds', 'polyline')}),
        ('ETA & Traffic', {'fields': ('current_eta', 'traffic_delay_minutes')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )