from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['id', 'driver', 'make', 'model', 'license_plate', 'status']
    list_filter = ['status', 'vehicle_type']
    search_fields = ['make', 'model', 'license_plate']
    readonly_fields = ['created_at', 'updated_at']