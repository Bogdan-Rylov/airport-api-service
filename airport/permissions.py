from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_staff)


class IsAdminOrAllowAnyReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user.is_authenticated and request.user.is_staff)
            or (request.method in SAFE_METHODS)
        )
