from django.urls import path
from . import views

urlpatterns = [
    path("<str:link_id>", views.go_to_link)
]
