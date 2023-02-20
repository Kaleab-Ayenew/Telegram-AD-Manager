from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User

import uuid
from datetime import datetime

from channels.models import TelegramChannel


class ScheduledPost(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    destination_channel = models.ForeignKey(
        TelegramChannel, on_delete=models.CASCADE)
    post_content = models.TextField()
    post_image_id = models.CharField(max_length=200, null=True)
    post_buttons = models.JSONField(blank=True, null=True)
    schedules = models.JSONField()
    created_at = models.DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return f"{self.owner.username} : {self.post_content[:50]}"
