from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.post_action),
    path('auth/', views.login_view),
]
