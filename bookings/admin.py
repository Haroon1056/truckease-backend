from django.contrib import admin
from .models import Booking, BookingHistory

# Only register Booking model first
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'driver', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_status']
    search_fields = ['customer__email', 'driver__email']
    readonly_fields = ['created_at', 'updated_at']

# Temporarily disable BookingHistory admin
# @admin.register(BookingHistory)
# class BookingHistoryAdmin(admin.ModelAdmin):
#     list_display = ['booking', 'status', 'created_at']