from rest_framework.permissions import BasePermission


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
        try:
            user = request.user.securityuser
        except Exception:
            return False
        return user and request.user.is_authenticated
