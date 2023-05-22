from django.db import models
from django.utils.crypto import get_random_string


def get_link_id():
    while True:
        id = get_random_string(8)
        if not ShortLink.objects.filter(link_id=id).exists():
            return id


class ShortLink(models.Model):
    link_id = models.CharField(
        max_length=8, primary_key=True, default=get_link_id, editable=False)
    long_link = models.URLField(max_length=200)

    def __str__(self):
        return f"{self.link_id} | {self.long_link}"
