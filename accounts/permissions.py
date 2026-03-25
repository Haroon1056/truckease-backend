from rest_framework import permissions

class IsDriver(permissions.BasePermission):
    """Allow access only to drivers"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'driver'

class IsAdmin(permissions.BasePermission):
    """Allow access only to admins"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'admin'

class IsCustomer(permissions.BasePermission):
    """Allow access only to customers"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'customer'

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow access only to owners or admin"""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to owner or admin
        return obj.driver == request.user or request.user.user_type == 'admin'