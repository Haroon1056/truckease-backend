from django.contrib import admin
from .models import LocationUpdate, TripRoute

@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'booking', 'latitude', 'longitude', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['vehicle__license_plate', 'booking__id']
    readonly_fields = ['timestamp']

@admin.register(TripRoute)
class TripRouteAdmin(admin.ModelAdmin):
    list_display = ['booking', 'distance_meters', 'duration_seconds', 'created_at']
    search_fields = ['booking__id']