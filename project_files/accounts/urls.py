from django.urls import path
from . import views

urlpatterns = [
    path('authorize/', views.auth_view, name="auth_url")
]
