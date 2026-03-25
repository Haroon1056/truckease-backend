from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    # Remove fieldsets - let Django handle it
    pass

admin.site.register(User, UserAdmin)