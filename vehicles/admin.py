from django.contrib import admin
from .models import Vehicle

class VehicleAdmin(admin.ModelAdmin):
    pass

admin.site.register(Vehicle, VehicleAdmin)