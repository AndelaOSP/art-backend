# Third-Party Imports
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsApiUser(BasePermission):
    """
    Allows access only to API users.
    """

    def has_permission(self, request, view):
        try:
            app = request.auth.application
        except Exception:
            return False
        return app and not request.auth.user


class IsSecurityUser(BasePermission):
    """
    Allows access only to security users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_securityuser


class IsSuperAdmin(BasePermission):
    """
    Allows access only to superuser.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser


class IsAdminReadOnly(BasePermission):
    """
    Allows read acess to none superusers.
    """

    def has_permission(self, request, view):
        return request.user.is_staff and request.method in SAFE_METHODS
