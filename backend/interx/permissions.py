from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """
    Allows access only to authenticated users with ADMIN role.
    """
    message = "Admin access required. You do not have permission to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "ADMIN"
        )


class IsStudentRole(permissions.BasePermission):
    """
    Allows access only to authenticated users with STUDENT role.
    """
    message = "Student access required. You do not have permission to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "STUDENT"
        )


class IsAdminOrStudentReadOnly(permissions.BasePermission):
    """
    Admins have full access.
    Students have read-only access (with visibility filtered at view/queryset level).
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return getattr(request.user, "role", None) == "ADMIN"
