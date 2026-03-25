from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['id', 'driver', 'make', 'model', 'license_plate', 'vehicle_type', 'status', 'is_available', 'created_at']
    list_filter = ['vehicle_type', 'status', 'is_available', 'year']
    search_fields = ['make', 'model', 'license_plate', 'driver__email', 'current_city']
    readonly_fields = ['created_at', 'updated_at', 'verified_at']
    
    fieldsets = (
        ('Owner Information', {
            'fields': ('driver',)
        }),
        ('Vehicle Details', {
            'fields': ('vehicle_type', 'make', 'model', 'year', 'license_plate', 'color')
        }),
        ('Capacity & Dimensions', {
            'fields': ('capacity_tons', 'dimensions')
        }),
        ('Description & Features', {
            'fields': ('description', 'features')
        }),
        ('Images', {
            'fields': ('front_image', 'back_image', 'side_image', 'interior_image'),
            'classes': ('collapse',)
        }),
        ('Location', {
            'fields': ('current_city', 'current_area', 'latitude', 'longitude')
        }),
        ('Pricing', {
            'fields': ('base_price_per_km', 'base_price_per_hour', 'waiting_charge_per_hour')
        }),
        ('Status & Verification', {
            'fields': ('status', 'verification_notes', 'verified_by', 'verified_at')
        }),
        ('Availability', {
            'fields': ('is_available', 'available_from', 'available_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['verify_vehicles', 'reject_vehicles']
    
    def verify_vehicles(self, request, queryset):
        """Admin action to verify selected vehicles"""
        for vehicle in queryset:
            vehicle.verify(request.user, "Verified by admin")
        self.message_user(request, f"{queryset.count()} vehicle(s) verified successfully.")
    verify_vehicles.short_description = "Verify selected vehicles"
    
    def reject_vehicles(self, request, queryset):
        """Admin action to reject selected vehicles"""
        for vehicle in queryset:
            vehicle.reject(request.user, "Rejected by admin")
        self.message_user(request, f"{queryset.count()} vehicle(s) rejected.")
    reject_vehicles.short_description = "Reject selected vehicles"