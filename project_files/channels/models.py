from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class TelegramChannel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    ch_username = models.CharField(max_length=150, unique=True)
    ch_id = models.IntegerField(unique=True)
    ch_photo_id = models.CharField(max_length=300)
    ch_member_count = models.IntegerField()

    def __str__(self):
        return self.ch_username
