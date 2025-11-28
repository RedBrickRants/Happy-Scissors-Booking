# users/permissions.py
from rest_framework import permissions

class IsAdminUserCustomType(permissions.BasePermission):
    """
    Custom permission that checks the user_type field.
    This replaces the manual check inside the view functions.
    """
    def has_permission(self, request, view):
        # We know request.user is authenticated here due to the token
        if request.user and request.user.is_authenticated:
            # Explicitly call the method that you confirmed works in the shell
            return request.user.is_admin_user()
        return False