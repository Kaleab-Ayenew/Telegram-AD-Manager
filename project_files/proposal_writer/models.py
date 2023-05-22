from django.db import models

# Create your models here.


class ProposalBotUser(models.Model):
    user_id = models.CharField(primary_key=True, max_length=20)
    user_first_name = models.CharField(max_length=100)

    def __str__(self):
        return self.user_first_name

