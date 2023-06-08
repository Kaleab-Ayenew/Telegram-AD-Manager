from django.db import models
from django.contrib.auth.models import User


class SocialManagerUser(models.Model):
    main_user = models.OneToOneField(User, on_delete=models.CASCADE)


class FacebookData(models.Model):
    owner = models.OneToOneField(
        'SocialManagerUser', related_name='facebook_data', on_delete=models.CASCADE)
    # long_term_token = models.CharField(max_length=500)
    page_access_token = models.CharField(max_length=500)
    page_id = models.CharField(max_length=20)


class TelegramData(models.Model):
    owner = models.OneToOneField(
        'SocialManagerUser', related_name='telegram_data', on_delete=models.CASCADE)
    manager_bot_token = models.CharField(max_length=150)
    channel_username = models.CharField(max_length=100)
    

