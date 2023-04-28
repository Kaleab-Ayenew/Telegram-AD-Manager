from django.contrib import admin
from .models import BotUser, ConnectedChannels, TempData


# Register your models here.
admin.site.register(BotUser)
admin.site.register(ConnectedChannels)
admin.site.register(TempData)
