from rest_framework import serializers
from urllib.parse import urlparse, parse_qs
import json
from .models import Seller, Product, ChapaBank, Sale, TemporarySellerData, TempDownloadLink, WithdrawRequest, YoutubeSale, YoutubeVideo, YoutubeVideoClient
from . import validators as myvalidators
from . import utils
from markdownify import markdownify as md


class UserCreateSerializer(serializers.Serializer):
    email = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class PaymentInfoSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    phone_no = serializers.CharField(max_length=10)


class VideoPaymentInfoSerializer(serializers.Serializer):
    phone_no = serializers.CharField(max_length=10)


class TempSellerSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ["verification_code"]
        extra_kwargs = {"seller_password": {"write_only": True}}
        model = TemporarySellerData


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Seller


class ProductSerializer(serializers.ModelSerializer):
    product_file = serializers.FileField(
        validators=[myvalidators.FileValidator(allowed_types=['application/zip', 'application/vnd.rar', 'application/x-rar'])])
    product_thumbnail = serializers.FileField(
        validators=[myvalidators.FileValidator(allowed_types=['image/jpeg', 'image/png'])])

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('product_file', None)

        return representation

    class Meta:
        exclude = ["product_seller"]
        extra_kwargs = {
            "product_seller": {
                "write_only": True
            },
            "product_file": {
                "write_only": True
            }}
        model = Product


class PublicProductSerializer(serializers.ModelSerializer):
    product_file = serializers.FileField(
        validators=[myvalidators.FileValidator(allowed_types=['application/zip', 'application/vnd.rar', 'application/x-rar'])])
    product_thumbnail = serializers.FileField(
        validators=[myvalidators.FileValidator(allowed_types=['image/jpeg', 'image/png'])])

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('product_file', None)
        markdown_description = md(representation.get("product_description"))
        representation.update({'product_description': markdown_description})
        return representation

    class Meta:
        exclude = ["product_seller"]
        extra_kwargs = {
            "product_seller": {
                "write_only": True
            },
            "product_file": {
                "write_only": True
            }}
        model = Product


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ChapaBank


class SaleSerilizer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Sale


class TempLinkSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = TempDownloadLink


class WithdrawInfoSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ["seller"]
        extra_kwargs = {"seller": {
            "write_only": True
        }}
        model = WithdrawRequest


class SaleStatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sale
        exclude = ['id', 'chapa_transaction_ref']


class ProductStatSerializer(serializers.ModelSerializer):
    product_sales = SaleStatSerializer(many=True, read_only=True)

    class Meta:
        fields = ['product_name', 'product_sales',
                  'product_price', 'product_id']
        model = Product


class YoutubeSaleSerializer(serializers.ModelSerializer):

    class Meta:
        fields = "__all__"
        model = YoutubeSale


class VideoStatSerializer(serializers.ModelSerializer):
    video_sales = YoutubeSaleSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        video_id = representation.get("video_id")
        video_info = representation.get("video_info")
        print(video_info)
        representation.pop("video_id")
        number_price = float(representation.get("video_price"))
        representation.update(
            {"video_info": json.loads(video_info), "n_price": number_price})
        return representation

    class Meta:
        fields = "__all__"
        model = YoutubeVideo


class YoutubeClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = YoutubeVideoClient
        exclude = ["main_user"]
        extra_kwargs = {
            "main_user": {
                "write_only": True
            }
        }


class ClientYoutubeVideoSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        video_id = representation.get("video_id")
        video_info = representation.get("video_info")
        print(video_info)
        representation.pop("video_id")
        number_price = float(representation.get("video_price"))
        total_sales = YoutubeSale.objects.filter(
            sold_video=instance, completed=True).all()
        total_sales_amount = len(total_sales)
        representation.update(
            {"video_info": json.loads(video_info), "n_price": number_price, "sales": total_sales_amount})
        return representation

    class Meta:
        exclude = ["video_owner"]
        extra_kwargs = {
            "video_owner": {
                "write_only": True
            }
        }
        model = YoutubeVideo


class SellerYoutubeVideoSerializer(serializers.ModelSerializer):

    def save(self, **kwargs):
        video_url = self.validated_data.get("video_id")
        parsed_url = urlparse(video_url)
        video_id = parse_qs(parsed_url.query).get('v')[0]

        video_info = utils.get_youtube_video_info(video_id)
        self.validated_data.update(
            {"video_id": video_id, "video_info": json.dumps(video_info)})

        return super().save(**kwargs)

    def update(self, instance, validated_data, **kwargs):
        video_id = validated_data.get(
            "video_id", instance.video_id)
        instance.video_id = video_id
        instance.video_info = json.dumps(
            utils.get_youtube_video_info(video_id))
        instance.video_price = validated_data.get(
            "video_price", instance.video_price)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        video_id = representation.get("video_id")
        video_info = json.loads(representation.get("video_info"))
        representation.update(
            {"video_link": f"https://youtube.com/watch?v={instance.video_id}", "video_info": video_info})
        return representation

    class Meta:
        exclude = ["video_owner"]
        extra_kwargs = {
            "video_owner": {
                "write_only": True
            }
        }
        model = YoutubeVideo


class PurchasedVideoSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        video_id = representation.get("video_id")

        video_info = representation.get("video_info")
        total_sales = YoutubeSale.objects.filter(
            sold_video=instance, completed=True).all()
        total_sales_amount = len(total_sales)
        representation.pop("video_id")
        number_price = float(representation.get("video_price"))
        representation.update(
            {"video_info": json.loads(video_info), "n_price": number_price, "sales": total_sales_amount})
        representation.update(
            {"v_stamp": utils.rot_encrypt(instance.video_id)})

        return representation

    class Meta:
        exclude = ["video_owner"]
        extra_kwargs = {
            "video_owner": {
                "write_only": True
            }
        }
        model = YoutubeVideo


class ClientRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    password = serializers.CharField()


class ClientLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    password = serializers.CharField()
