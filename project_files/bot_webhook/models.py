from django.db import models

# Create your models here.


class SampleDB(models.Model):
    names = models.CharField(max_length=400)
