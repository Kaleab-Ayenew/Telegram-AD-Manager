from rest_framework import serializers
from .models import Product, ProductImage, Discount, Review, Order
from django.utils import timezone
from datetime import timedelta
from statistics import mean


class OrderSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()

    class Meta:
        fields = "__all__"
        extra_kwargs = {
            "order_product": {
                "write_only": True
            }
        }
        model = Order


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = ProductImage


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Discount


class ProductSerializer(serializers.ModelSerializer):
    # images = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    # discount = serializers.PrimaryKeyRelatedField(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    discount = DiscountSerializer(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        orders = instance.orders.all()
        month_ago = timezone.now() - timedelta(days=30)
        past_month_orders = instance.orders.filter(order_time__gte=month_ago)
        completed_orders = instance.orders.filter(order_status='completed')

        is_new = instance.created > (timezone.now() - timedelta(days=3))

        best_sell = len(orders) > 10
        trending = len(past_month_orders) > 10
        total_sold = len(completed_orders)

        rating_no = len(instance.reviews.all())
        rating_score = mean(
            [r.review_score for r in instance.reviews.all()]) if instance.reviews.all() else 0
        data.update({'best_sell': best_sell, 'trending': trending,
                    'total_sold': total_sold, 'rating_no': rating_no, 'rating_score': rating_score, "is_new": is_new})
        return data

    class Meta:
        model = Product
        fields = ['images',
                  'discount',
                  'social_image',
                  "title",
                  "slug",
                  "price",
                  "desc",
                  "condition",
                  "vendor",
                  "brand",
                  "category",
                  "featured",
                  "weight",
                  "tags",
                  "stock",
                  "created",
                  "additional_info",
                  "processor_type",
                  "processor_model",
                  "processor_speed",
                  "storage_type",
                  "storage_size",
                  "ram_model",
                  "ram_size",
                  "graphics_card"]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

# class FacebookLinkSerializer(serializers.Serializer):
