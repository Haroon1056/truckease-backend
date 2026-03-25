from django.contrib import admin
from .models import LocationUpdate, TripRoute

# Temporarily disable all tracking admin
# @admin.register(LocationUpdate)
# class LocationUpdateAdmin(admin.ModelAdmin):
#     list_display = ['vehicle', 'booking', 'timestamp']

# @admin.register(TripRoute)
# class TripRouteAdmin(admin.ModelAdmin):
#     list_display = ['booking', 'distance_meters']