from django.urls import path
from .views import invite_bot_requests, proxy_bot_request

urlpatterns = [
    path("invite-bot/", invite_bot_requests, name="invite-bot-url"),
    path("proxy-bot/", proxy_bot_request, name="proxy-bot-url"),
]
