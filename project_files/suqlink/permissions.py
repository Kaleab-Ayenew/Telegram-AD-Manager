from rest_framework.permissions import IsAuthenticated
from .models import Seller, YoutubeVideoClient
from . import utils


class IsSeller(IsAuthenticated):
    message = "You don't have permission to access this data."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return Seller.objects.filter(main_user=request.user).exists()


class IsProductOwner(IsSeller):
    message = "You don't have permissions to perform this action"

    def has_object_permission(self, request, view, obj):
        return request.user == obj.product_seller.main_user


class IsVideoClient(IsAuthenticated):
    message = "You don't have permission to perform this action"

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return YoutubeVideoClient.objects.filter(main_user=request.user).exists()


class HasPurchasedVideo(IsVideoClient):
    def has_object_permission(self, request, view, obj):

        result = utils.user_has_purchased_video(
            main_user=request.user, video=obj)
        return utils.user_has_purchased_video(main_user=request.user, video=obj)


class IsVideoOwner(IsSeller):
    message = "You don't have permissions to perform this action"

    def has_object_permission(self, request, view, obj):
        return request.user == obj.video_owner.main_user
