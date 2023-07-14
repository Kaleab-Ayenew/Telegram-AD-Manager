from rest_framework.permissions import IsAuthenticated
from .models import Seller


class IsSeller(IsAuthenticated):
    message = "You don't have permission to access this data."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return Seller.objects.filter(main_user=request.user).exists()
