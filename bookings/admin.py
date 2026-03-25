from django.contrib import admin
from .models import Booking, BookingHistory

class BookingAdmin(admin.ModelAdmin):
    # No custom fields - let Django handle
    pass

class BookingHistoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Booking, BookingAdmin)
admin.site.register(BookingHistory, BookingHistoryAdmin)