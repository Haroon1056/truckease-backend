from django.contrib import admin
from .models import Vehicle

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'driver', 'make', 'model', 'license_plate', 'status', 'is_available')
    list_filter = ('status', 'vehicle_type', 'is_available')
    search_fields = ('make', 'model', 'license_plate', 'driver__email')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Vehicle, VehicleAdmin)