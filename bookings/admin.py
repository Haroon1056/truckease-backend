from django.contrib import admin
from .models import Booking, BookingHistory

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'driver', 'status', 'total_amount', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'is_hazardous']
    search_fields = ['customer__email', 'driver__email', 'pickup_address', 'dropoff_address', 'cargo_type']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer',)
        }),
        ('Driver & Vehicle', {
            'fields': ('driver', 'vehicle')
        }),
        ('Trip Details', {
            'fields': ('pickup_address', 'pickup_latitude', 'pickup_longitude', 
                      'dropoff_address', 'dropoff_latitude', 'dropoff_longitude')
        }),
        ('Cargo Information', {
            'fields': ('cargo_type', 'cargo_weight', 'cargo_description', 'is_hazardous')
        }),
        ('Schedule', {
            'fields': ('pickup_time', 'estimated_delivery_time', 'actual_pickup_time', 'actual_delivery_time')
        }),
        ('Pricing', {
            'fields': ('distance_km', 'base_fare', 'distance_charge', 'waiting_charge', 'total_amount')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status', 'payment_id')
        }),
        ('Status', {
            'fields': ('status', 'cancellation_reason', 'cancelled_by')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'driver_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-set total_amount before saving"""
        if not obj.total_amount:
            obj.total_amount = obj.calculate_total()
        super().save_model(request, obj, form, change)

@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ['booking', 'status', 'changed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['booking__id', 'changed_by__email']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('History', {
            'fields': ('booking', 'status', 'changed_by', 'notes', 'created_at')
        }),
    )