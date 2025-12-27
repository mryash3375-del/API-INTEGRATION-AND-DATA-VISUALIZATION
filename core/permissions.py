from rest_framework import permissions

class IsRestaurantOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a restaurant to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        # obj could be a Restaurant, or a MenuItem (via obj.category.restaurant)
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'restaurant'):
            return obj.restaurant.owner == request.user
        if hasattr(obj, 'category'):
            return obj.category.restaurant.owner == request.user

        return False
