from rest_framework import serializers
from .models import Seller, Product, ChapaBank, Sale, TemporarySellerData, TempDownloadLink


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
        fields = "__all__"
        model = TemporarySellerData


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Seller


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ["product_seller"]
        extra_kwargs = {"product_seller": {
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
