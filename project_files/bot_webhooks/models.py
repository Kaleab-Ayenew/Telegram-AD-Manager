from django.db import models

# Create your models here.


class TelegramUser(models.Model):
    tg_user_id = models.CharField(max_length=50)
    first_name = models.CharField(max_length=150)
    invited_by = models.CharField(max_length=50)
    invited_number = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} : {self.invited_number} people"
