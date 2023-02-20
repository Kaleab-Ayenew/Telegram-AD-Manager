from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserData(models.Model):
    main_user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    tg_username = models.CharField(
        max_length=150, unique=True, default=None, null=True)
    photo_url = models.URLField(max_length=500, default=None, null=True)

    def __str__(self):
        return self.main_user.first_name
