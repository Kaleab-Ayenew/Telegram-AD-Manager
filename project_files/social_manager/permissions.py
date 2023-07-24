from rest_framework.permissions import IsAuthenticated
from .models import SocialManagerUser

# Extends the IsAuthenticated permission class to enable object level permission checking


class IsAuthAndOwnsObject(IsAuthenticated):

    message = "You don't have permission to acess this data."

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return request.user == obj.owner


class IsSocialManagerUser(IsAuthenticated):
    message = "You don't have permission to access this data."
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return SocialManagerUser.objects.filter(main_user=request.user).exists()
