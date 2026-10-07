from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the author of a comment to edit or delete it.
    Read permissions are allowed to any request.
    """

    def has_permission(self, request, view):
        # Allow safe methods to everyone; mutations require authentication
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Mutation permissions are strictly restricted to the comment author
        return obj.author == request.user
