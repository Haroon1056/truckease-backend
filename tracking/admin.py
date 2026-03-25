from django.contrib import admin
from .models import LocationUpdate, TripRoute

class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'booking', 'latitude', 'longitude', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('vehicle__license_plate',)

class TripRouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'distance_meters', 'duration_seconds', 'created_at')
    search_fields = ('booking__id',)

admin.site.register(LocationUpdate, LocationUpdateAdmin)
admin.site.register(TripRoute, TripRouteAdmin)