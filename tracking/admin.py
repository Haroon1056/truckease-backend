from django.contrib import admin
from .models import LocationUpdate, TripRoute

class LocationUpdateAdmin(admin.ModelAdmin):
    pass

class TripRouteAdmin(admin.ModelAdmin):
    pass

admin.site.register(LocationUpdate, LocationUpdateAdmin)
admin.site.register(TripRoute, TripRouteAdmin)