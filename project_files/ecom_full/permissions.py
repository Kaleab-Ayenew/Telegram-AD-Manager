from rest_framework.permissions import IsAuthenticated
from .models import EcomAdmin

# Extends the IsAuthenticated permission class to enable object level permission checking


class IsAuthAndOwnsObject(IsAuthenticated):

    message = "You don't have permission to acess this data."

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return request.user == obj.owner


class IsEcomAdmin(IsAuthenticated):
    message = "You don't have permission to access this data."

    def has_permission(self, request, view):
        return EcomAdmin.objects.filter(user=request.user).exists()
