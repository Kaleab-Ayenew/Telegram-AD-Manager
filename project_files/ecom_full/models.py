from typing import Iterable, Optional
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from uuid import uuid4
import time
# Create your models here.


def get_image_path(instance, filename):
    ext = filename.split(".")[-1]
    image_id = instance.id
    return f"neva_product_images/{instance.product.slug}/image_{image_id}.{ext}"


def get_social_image_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"neva_product_images/{instance.slug}/social_image/image_{int(time.time())}.{ext}"


class Product(models.Model):
    CONDITION_CHOICE = [
        ('new', 'new'),
        ('slightly used', 'slightly used'),
        ('used', 'used'),
    ]

    SIZE_CHOICE = [
        ('s', 's'),
        ('m', 'm'),
        ('l', 'l'),
    ]
    PROCESSOR_TYPE_OPTIONS = [
        ('Intel', 'Intel'),
        ('AMD', 'AMD')
    ]

    PROCESSOR_MODEL_OPTIONS = [
        ('core i3', 'core i3'),
        ('core i5', 'core i5'),
        ('core i7', 'core i7'),
        ('core i9', 'core i9')
    ]

    STORAGE_TYPE_OPTIONS = [
        ('SSD', 'SSD'),
        ('HDD', 'HDD')
    ]

    RAM_MODEL_OPTIONS = [
        ('DDR3', 'DDR3'),
        ('DDR4', 'DDR4')
    ]

    title = models.CharField(max_length=200)
    unique_id = models.UUIDField(default=uuid4, editable=False)
    social_image = models.ImageField(
        upload_to=get_social_image_path, max_length=150, null=True)
    slug = models.SlugField(max_length=200, editable=False,
                            unique=True, primary_key=True)
    # moreLove = models.BooleanField()
    price = models.IntegerField()
    # oldPrice = models.IntegerField(null=True, blank=True)
    desc = models.TextField()
    totalSell = models.IntegerField(default=0)
    condition = models.CharField(
        max_length=15,
        choices=CONDITION_CHOICE,
        default='brand new',
    )
    vendor = models.CharField(max_length=25, default="Neva Computers")
    # color = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    category = models.CharField(max_length=50)
    featured = models.BooleanField()

    # # Set this when the product is sent to the user
    # trending = models.BooleanField(default=False)

    # variations = models.JSONField(null=True)

    weight = models.IntegerField()
    tags = models.JSONField(null=True)

    # size = models.CharField(
    #     max_length=1, choices=SIZE_CHOICE, default='m')

    stock = models.IntegerField()

    # rating = models.IntegerField()
    # ratingScore = models.IntegerField()

    # Newly added fields
    processor_type = models.CharField(
        max_length=10, choices=PROCESSOR_TYPE_OPTIONS)
    processor_model = models.CharField(
        max_length=10, choices=PROCESSOR_MODEL_OPTIONS)
    processor_speed = models.DecimalField(max_digits=2, decimal_places=1)

    storage_type = models.CharField(max_length=5, choices=STORAGE_TYPE_OPTIONS)
    storage_size = models.IntegerField()

    ram_model = models.CharField(max_length=10, choices=RAM_MODEL_OPTIONS)
    ram_size = models.IntegerField()

    graphics_card = models.CharField(max_length=50)

    created = models.DateTimeField(auto_now_add=True)

    additional_info = models.JSONField(null=True)

    def save(self, *args, **kwargs):
        self.slug = "-".join(self.title.lower().split(" ")
                             ) + "-" + str(self.unique_id)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Review(models.Model):
    product = models.ForeignKey(
        Product, related_name='reviews', on_delete=models.CASCADE)
    review_text = models.TextField(null=True)
    review_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)])

    def __str__(self):
        return f'Review [{self.review_score}]: {self.product.title}'


class Discount(models.Model):
    product = models.OneToOneField(
        Product, related_name='discount', on_delete=models.CASCADE)
    percentage = models.IntegerField()
    expireDate = models.DateField(null=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        active = 'Active' if self.isActive else 'Inactive'
        return f'[{active}]: [{self.percentage}]% OFF {self.product.title}'


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name='images', on_delete=models.CASCADE)
    img = models.ImageField(upload_to=get_image_path, max_length=150)

    def __str__(self):
        return f'Image: {self.product.title}'


class Order(models.Model):
    PAYMENT_METHOD_OPTIONS = [
        ('chapa', 'chapa'),
        ('cash', 'cash')
    ]

    PAYMENT_STATUS_OPTIONS = [
        ('unpaid', 'unpaid'),
        ('pending', 'pending'),
        ('paid', 'paid')
    ]

    ORDER_STATUS_OPTIONS = [
        ('pending', 'pending'),
        ('completed', 'completed')
    ]
    order_product = models.ForeignKey(
        Product, related_name='orders', on_delete=models.CASCADE)
    order_amount = models.IntegerField(default=1)

    total_price = models.IntegerField(editable=False)

    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=10)
    customer_email = models.EmailField(max_length=100)

    payment_method = models.CharField(
        max_length=30, choices=PAYMENT_METHOD_OPTIONS, default='cash')
    # payment_status = models.CharField(
    #     max_length=15, choices=PAYMENT_STATUS_OPTIONS, default='unpaid')

    order_time = models.DateTimeField(auto_now_add=True)

    order_status = models.CharField(
        max_length=15, choices=ORDER_STATUS_OPTIONS, default='pending')

    def __str__(self):
        return f"{self.order_product.title} | {self.order_amount} - ETB {self.total_price} | {self.order_status}"

    def save(self, *args, **kwargs):
        self.total_price = self.order_product.price * self.order_amount
        super(Order, self).save(*args, **kwargs)


class EcomAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
