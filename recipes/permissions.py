from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCreatorOrReadOnly(BasePermission):
    """Only creators can create recipes. Anyone can read public ones."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_creator

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # Only the recipe's author can edit or delete it
        return obj.author == request.user


class IsOwnerOrReadOnly(BasePermission):
    """Object-level: only the owner can modify their own objects."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class IsAdminUser(BasePermission):
    """Only platform admins can access this view."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_platform_admin