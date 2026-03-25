from django.contrib import admin
from .models import Booking, BookingHistory

admin.site.register(Booking)
admin.site.register(BookingHistory)