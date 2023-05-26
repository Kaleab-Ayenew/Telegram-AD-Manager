from django.urls import path
from . import views

urlpatterns = [
    path('admin/', views.channel_admin_bot),
    path('info/', views.info_bot),
]
