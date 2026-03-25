from django.contrib import admin
from .models import Booking, BookingHistory

# Simplified Booking Admin
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_status')
    search_fields = ('customer__email',)
    readonly_fields = ('created_at', 'updated_at')

# Simplified BookingHistory Admin
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ('booking', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('booking__id',)

admin.site.register(Booking, BookingAdmin)
admin.site.register(BookingHistory, BookingHistoryAdmin)