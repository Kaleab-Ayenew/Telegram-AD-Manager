from django.contrib import admin
from .models import SocialManagerUser, FacebookData, TelegramData
# Register your models here.
admin.site.register(SocialManagerUser)
admin.site.register(FacebookData)
admin.site.register(TelegramData)
