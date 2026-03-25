from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['id', 'driver', 'make', 'model', 'license_plate', 'vehicle_type', 'status', 'is_available']
    list_filter = ['vehicle_type', 'status', 'is_available', 'year']
    search_fields = ['make', 'model', 'license_plate', 'driver__email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Owner', {'fields': ('driver',)}),
        ('Vehicle Details', {'fields': ('vehicle_type', 'make', 'model', 'year', 'license_plate', 'color')}),
        ('Capacity', {'fields': ('capacity_tons', 'dimensions')}),
        ('Location', {'fields': ('current_city', 'current_area', 'latitude', 'longitude')}),
        ('Pricing', {'fields': ('base_price_per_km', 'base_price_per_hour', 'waiting_charge_per_hour')}),
        ('Status', {'fields': ('status', 'is_available', 'verification_notes')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )