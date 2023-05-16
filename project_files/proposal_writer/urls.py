from django.urls import path
from . import views

urlpatterns = [
    path('get-proposal/', views.get_proposal),
]
