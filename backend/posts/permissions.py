from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the author of a post to edit or delete it.
    Safe methods (GET, HEAD, OPTIONS) are permitted for any user (public).
    """

    def has_permission(self, request, view):
        # Allow safe methods to everyone; writing requires authentication
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write/delete permissions are strictly restricted to the author
        return obj.author == request.user
