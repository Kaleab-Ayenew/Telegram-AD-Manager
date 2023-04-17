from django.urls import path
from . import views
urlpatterns = [
    path('pay/', views.chapa_pay, name="chapa-payment-url"),
    path('callback/', views.chapa_callback, name="chapa-callback-url"),
]
