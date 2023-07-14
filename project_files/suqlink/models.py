from django.db import models
from uuid import uuid4
import time
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Helper functions


def get_product_thumb_path(instance, filename):
    ext = filename.split(".")[-1]
    time_stamp = int(time.time())
    return f"suqlink-static/product-image/{time_stamp}.{ext}"


def get_seller_photo_path(instance, filename):
    ext = filename.split(".")[-1]
    time_stamp = int(time.time())
    return f"suqlink-static/profile-image/{time_stamp}.{ext}"


def get_product_file_path(instance, filename):
    ext = filename.split(".")[-1]
    time_stamp = int(time.time())
    unique_id = str(uuid4())
    return f"suqlink-static/products/{unique_id}/{time_stamp}.{ext}"


def get_product_id():
    while True:
        id = get_random_string(10)
        if not Product.objects.filter(product_id=id).exists():
            return id


def get_templink_id():
    while True:
        id = get_random_string(10)
        if not TempDowloadLink.objects.filter(link_id=id).exists():
            return id


class TemporarySellerData(models.Model):
    temp_data_uuid = models.UUIDField(
        default=uuid4, editable=False, primary_key=True)
    seller_username = models.CharField(max_length=100)
    seller_password = models.CharField(max_length=100)
    seller_email = models.EmailField(max_length=15)
    bank_account_full_name = models.CharField(max_length=200)
    bank_account_number = models.CharField(max_length=50)
    bank_provider = models.UUIDField()
    temp_data_timestamp = models.DateTimeField(auto_now_add=True)
    verification_code = models.CharField(max_length=8, null=True)


class Seller(models.Model):
    main_user = models.OneToOneField(
        'User', on_delete=models.CASCADE, related_name='__sellers')
    seller_username = models.CharField(max_length=100, primary_key=True)
    seller_photo = models.ImageField(
        upload_to=get_seller_photo_path, null=True)
    seller_timestamp = models.DateTimeField(auto_now_add=True)
    bank_account_full_name = models.CharField(max_length=200)
    bank_account_number = models.CharField(max_length=50)
    bank_provider = models.ForeignKey(
        'ChapaBanks', on_delete=models.RESTRICT, related_name='this_bank_sellers')
    chapa_subaccount_id = models.UUIDField(null=True)


class ChapaBank(models.Model):
    chapa_bank_id = models.UUIDField(primary_key=True)
    bank_name = models.CharField(max_length=100)


class Product(models.Model):
    product_seller = models.ForeignKey(
        'Seller', on_delete=models.CASCADE, related_name='__products')
    product_id = models.CharField(
        max_length=10, default=get_product_id, editable=False)
    product_name = models.CharField(max_length=200)
    product_thumbnail = models.ImageField(
        upload_to=get_product_thumb_path, max_length=200)
    product_description = models.TextField()
    product_price = models.IntegerField()
    product_file = models.FileField(
        upload_to=get_product_file_path, max_length=200)
    product_timestamp = models.DateTimeField(auto_now_add=True)


class Sale(models.Model):
    sold_product = models.ForeignKey('Product', on_delete=models.CASCADE)
    sale_timestamp = models.DateTimeField(auto_now_add=True)
    chapa_transaction_ref = models.UUIDField(null=True)
    completed = models.BooleanField(default=False)


class TempDownloadLink(models.Model):
    link_id = models.CharField(
        max_length=10, default=get_templink_id, editable=False, primary_key=True)
    sale = models.OneToOneField(
        'Sale', on_delete=models.CASCADE, related_name="temp_link")

    time_stamp = models.DateTimeField(auto_now_add=True)
    was_user = models.BooleanField(default=False)

    def is_expired(self):
        now = timezone.now()
        diff = now - self.time_stamp
        if diff > timedelta(minutes=5):
            return True
        else:
            return False

    def link_string(self):
        l = f"{settings.HOST_URL}download/{self.link_id}"
        return l

    def __str__(self):
        l = f"{settings.HOST_URL}download/{self.link_id}"
        return l
