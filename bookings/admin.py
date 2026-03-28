from django.contrib import admin
from .models import Booking, BookingHistory


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Booking Admin for TruckEase
    Manage all trip bookings
    """
    
    # Display fields in the list view
    list_display = (
        'id',
        'customer',
        'driver',
        'status',
        'total_amount',
        'payment_status',
        'pickup_time',
        'created_at'
    )
    
    # Filters for sidebar
    list_filter = (
        'status',
        'payment_status',
        'is_hazardous',
        'pickup_time',
        'created_at'
    )
    
    # Searchable fields
    search_fields = (
        'customer__email',
        'driver__email',
        'pickup_address',
        'dropoff_address',
        'cargo_type'
    )
    
    # Default ordering
    ordering = ('-created_at',)
    
    # Read-only fields
    readonly_fields = ('created_at', 'updated_at')
    
    # Organize fields into sections
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer',)
        }),
        ('Driver & Vehicle', {
            'fields': ('driver', 'vehicle')
        }),
        ('Trip Details', {
            'fields': (
                'pickup_address', 
                'pickup_latitude', 
                'pickup_longitude',
                'dropoff_address', 
                'dropoff_latitude', 
                'dropoff_longitude'
            )
        }),
        ('Cargo Information', {
            'fields': (
                'cargo_type', 
                'cargo_weight', 
                'cargo_description',
                'is_hazardous'
            )
        }),
        ('Schedule', {
            'fields': (
                'pickup_time',
                'estimated_delivery_time',
                'actual_pickup_time',
                'actual_delivery_time'
            )
        }),
        ('Pricing', {
            'fields': (
                'distance_km',
                'base_fare',
                'distance_charge',
                'waiting_charge',
                'total_amount'
            )
        }),
        ('Payment', {
            'fields': (
                'payment_method',
                'payment_status',
                'payment_id'
            )
        }),
        ('Status & Notes', {
            'fields': (
                'status',
                'cancellation_reason',
                'cancelled_by',
                'customer_notes',
                'driver_notes'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    # Custom actions
    actions = ['mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected bookings as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} booking(s) marked as completed.')
    mark_as_completed.short_description = "Mark selected bookings as completed"
    
    def mark_as_cancelled(self, request, queryset):
        """Mark selected bookings as cancelled"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} booking(s) marked as cancelled.')
    mark_as_cancelled.short_description = "Mark selected bookings as cancelled"


@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    """
    Booking History Admin
    Track status changes of bookings
    """
    
    list_display = ('booking', 'status', 'changed_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('booking__id', 'changed_by__email')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('History Information', {
            'fields': ('booking', 'status', 'changed_by', 'notes', 'created_at')
        }),
    )