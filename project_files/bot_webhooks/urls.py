from django.urls import path
from .views import invite_bot_requests

urlpatterns = [
    path("", invite_bot_requests, name="invite-bot-url")
]
