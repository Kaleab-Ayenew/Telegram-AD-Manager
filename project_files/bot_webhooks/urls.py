from django.urls import path
from .views import invite_bot_requests, proxy_bot_request

urlpatterns = [
    path("invite-bot/", invite_bot_requests, name="invite-bot-url"),
    path("proxy-bot/", proxy_bot_request, name="proxy-bot-url"),
    path("chapa-bot/", proxy_bot_request, name="chapa-bot-url"),
    path("chapa-api-hook/", proxy_bot_request, name="chapa-hook-url"),
]
