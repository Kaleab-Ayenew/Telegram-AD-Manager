from rest_framework import serializers
from .models import Seller, Product, ChapaBank, Sale, TemporarySellerData, TempDownloadLink, WithdrawRequest
from . import validators as myvalidators
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
        validators=[myvalidators.FileValidator(allowed_types=['application/zip'])])
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
        validators=[myvalidators.FileValidator(allowed_types=['application/zip'])])
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
