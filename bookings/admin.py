from django.contrib import admin
from .models import Booking, BookingHistory

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'driver_id', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_status')
    search_fields = ('customer__email', 'driver__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fields = (
        'customer', 'driver', 'vehicle',
        'pickup_address', 'pickup_latitude', 'pickup_longitude',
        'dropoff_address', 'dropoff_latitude', 'dropoff_longitude',
        'cargo_type', 'cargo_weight', 'cargo_description', 'is_hazardous',
        'pickup_time', 'estimated_delivery_time',
        'distance_km', 'base_fare', 'distance_charge', 'waiting_charge', 'total_amount',
        'payment_method', 'payment_status', 'payment_id',
        'status', 'cancellation_reason', 'cancelled_by',
        'customer_notes', 'driver_notes',
        'created_at', 'updated_at'
    )

class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ('booking', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('booking__id',)
    readonly_fields = ('created_at',)

admin.site.register(Booking, BookingAdmin)
admin.site.register(BookingHistory, BookingHistoryAdmin)