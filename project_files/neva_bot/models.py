from django.db import models

# Create your models here.


class NevaBotInfo(models.Model):
    gps_link = models.URLField(max_length=100)
    account_info = models.TextField()
