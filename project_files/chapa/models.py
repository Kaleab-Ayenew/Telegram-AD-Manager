from django.db import models
import uuid


def get_image_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"product_images/{instance.unique_id}/image.{ext}"


class Product(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4)
    product_image = models.ImageField(
        upload_to=get_image_path, max_length=300, null=True)
    product_name = models.CharField(max_length=250, null=True)
    product_description = models.TextField(null=True)
    product_price = models.IntegerField(null=True)
    image_width = models.IntegerField(null=True)
    image_height = models.IntegerField(null=True)
    owner_telegram_id = models.BigIntegerField(null=True)
    target_channel_id = models.BigIntegerField(null=True)


class TempData(models.Model):
    current_product_id = models.CharField(
        max_length=50, null=True, unique=True)
    current_user = models.BigIntegerField(unique=True)
    question_index = models.IntegerField(default=0)

    class Meta:
        unique_together = ('current_product_id', 'current_user',)