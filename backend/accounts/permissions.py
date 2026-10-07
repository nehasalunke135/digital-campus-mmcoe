from rest_framework.permissions import BasePermission
from .models import User


class IsStudent(BasePermission):
    """
    Allows access only to authenticated users with the STUDENT role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.STUDENT
        )


class IsAdminUserRole(BasePermission):
    """
    Allows access only to authenticated users with the ADMIN role or superusers/staff.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == User.Role.ADMIN or request.user.is_staff or request.user.is_superuser)
        )


def HasRole(*allowed_roles):
    """
    Factory to construct a permission class checking for specific role(s).
    """
    class RolePermission(BasePermission):
        def has_permission(self, request, view):
            return bool(
                request.user and
                request.user.is_authenticated and
                request.user.role in allowed_roles
            )
    return RolePermission
