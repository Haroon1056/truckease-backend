from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin for TruckEase
    Uses email as the primary identifier, hides username from forms
    """
    
    # Display fields in the user list
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active', 'is_verified')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    
    # Fields to show when editing a user (username is hidden)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture', 'date_of_birth', 'address')
        }),
        ('User Type & Status', {
            'fields': ('user_type', 'is_verified')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    # Fields to show when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'user_type', 'phone_number'),
        }),
    )
    
    # Make these fields read-only
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        """Make email read-only when editing existing users"""
        if obj:  # Editing an existing user
            return self.readonly_fields + ('email',)
        return self.readonly_fields

# Register the User model with our custom admin
admin.site.register(User, CustomUserAdmin)