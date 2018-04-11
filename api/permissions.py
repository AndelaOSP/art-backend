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
