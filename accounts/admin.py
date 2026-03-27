from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin for TruckEase
    Optimized for email-based authentication
    """
    
    # Display fields in the user list
    list_display = (
        'email', 
        'first_name', 
        'last_name', 
        'user_type', 
        'phone_number',
        'is_verified', 
        'is_active',
        'created_at'
    )
    
    # Filters for the sidebar
    list_filter = (
        'user_type', 
        'is_verified', 
        'is_active', 
        'is_staff',
        'created_at'
    )
    
    # Searchable fields
    search_fields = (
        'email', 
        'first_name', 
        'last_name', 
        'phone_number'
    )
    
    # Default ordering
    ordering = ('-created_at',)
    
    # Fields to display when editing a user
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal Information'), {
            'fields': (
                'first_name', 
                'last_name', 
                'phone_number', 
                'profile_picture',
                'date_of_birth', 
                'address'
            )
        }),
        (_('User Type & Status'), {
            'fields': ('user_type', 'is_verified')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 
                'is_staff', 
                'is_superuser',
                'groups', 
                'user_permissions'
            )
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    # Fields to display when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'password1', 
                'password2',
                'first_name', 
                'last_name', 
                'user_type',
                'phone_number'
            )
        }),
    )
    
    # Read-only fields
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        """Make email read-only when editing existing users"""
        if obj:  # Editing an existing user
            return self.readonly_fields + ('email',)
        return self.readonly_fields