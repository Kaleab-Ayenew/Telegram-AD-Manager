from django.urls import path
from . import views
urlpatterns = [
    path('pay/', views.chapa_pay, name="chapa-payment-url"),
    path('callback/', views.chapa_callback, name="chapa-callback-url"),
    path('payment-webhook/', views.chapa_payment_webhook, name="chapa-webhook-url"),
    path('chapa-bot-webhook/', views.chapa_bot_webhook,
         name="chapa-pay-bot-webhook-url"),
    path('shop-manager-bot-webhook/', views.shop_manager_webhook,
         name="shop-manager-bot-webhook-url")
]
