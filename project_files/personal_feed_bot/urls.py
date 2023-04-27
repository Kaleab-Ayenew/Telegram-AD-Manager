from django.urls import path
from . import views

urlpatterns = [
    path('user-bot-webhook/', views.user_bot_webhook,
         name="personal-feed-user-bot"),
]
