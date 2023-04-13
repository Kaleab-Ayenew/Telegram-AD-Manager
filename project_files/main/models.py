from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User

import uuid
from datetime import datetime

from channels.models import TelegramChannel


def get_image_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"post_images/{instance.unique_id}/image.{ext}"


def get_img_default():
    return "post_images/081340a8-385e-4c12-a97b-48a4821f20f2/image.png"


def get_default_sdate():
    return datetime.fromisoformat("2023-04-13")


def get_default_edate():
    return datetime.fromisoformat("2023-04-14")


class ScheduledPost(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    destination_channel = models.ForeignKey(
        TelegramChannel, on_delete=models.CASCADE)
    post_content = models.TextField()
    post_image = models.ImageField(
        upload_to=get_image_path, max_length=300, default=get_img_default)
    post_buttons = models.JSONField(blank=True, null=True)
    start_date = models.DateField(default=get_default_sdate)
    end_date = models.DateField(default=get_default_edate)
    post_time = models.DateTimeField(default=datetime.now())
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.owner.username} : {self.post_content[:50]}"
