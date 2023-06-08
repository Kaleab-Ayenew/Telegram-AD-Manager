from django.db import models
from django.utils import timezone

from datetime import timedelta
import time

from personal_feed_bot.models import BotUser


def get_image_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"{instance.bot_name}_sub_images/{instance.sub_name}/image_{time.time()}.{ext}"


class FeedgramSubscription(models.Model):
    bot_user = models.OneToOneField(
        BotUser, on_delete=models.CASCADE, related_name='subscription')
    sub_level = models.ForeignKey(
        'FeedgramFeature', on_delete=models.CASCADE, related_name='subscribers')
    sub_period = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now=True)
    exp_date = models.DateTimeField()

    def is_active(self) -> bool:
        return self.exp_date > timezone.now()

    def days_left(self) -> int:
        if self.is_active():
            t_left = self.exp_date - timezone.now()
            return t_left.days
        else:
            return 0

    def __str__(self):
        return f"{self.bot_user.user_first_name} | {self.sub_period} | {self.sub_level} | {'Active' if self.is_active else 'Inactive'}"


class FeedgramFeature(models.Model):

    bot_name = models.CharField(max_length=50)
    sub_name = models.CharField(max_length=50)
    super_channels = models.IntegerField()
    channel_per_superchannel = models.IntegerField()
    price = models.IntegerField()
    poster_image = models.ImageField(upload_to=get_image_path, max_length=150)
    invoice_title = models.CharField(max_length=50)
    invoice_desc = models.TextField()

    def __str__(self):
        return f"{self.bot_name} | {self.sub_name} | {self.price} Birr"
