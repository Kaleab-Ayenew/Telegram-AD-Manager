from django.contrib import admin
from .models import BotUser, ConnectedChannels


# Register your models here.
admin.site.register(BotUser)
admin.site.register(ConnectedChannels)
