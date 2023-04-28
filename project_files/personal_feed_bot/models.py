from django.db import models

# Create your models here.


class BotUser(models.Model):
    user_id = models.CharField(primary_key=True, max_length=50)
    user_first_name = models.CharField(max_length=150)
    feed_channel_id = models.CharField(max_length=50, null=True)
    feed_channel_username = models.CharField(max_length=50, null=True)
    feed_channel_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.user_first_name} | {self.feed_channel_name}"


class ConnectedChannels(models.Model):
    owner_user = models.ForeignKey(
        BotUser, on_delete=models.CASCADE, related_name='connected_channels')
    channel_username = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.owner_user} | {self.channel_username}"

    class Meta:
        unique_together = ('owner_user', 'channel_username',)


class TempData(models.Model):
    active_user = models.CharField(max_length=50, unique=True)
    form_name = models.CharField(max_length=70)
    active_question = models.IntegerField(default=0)
