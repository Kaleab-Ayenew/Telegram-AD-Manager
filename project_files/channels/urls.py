from django.urls import path
from . import views
urlpatterns = [
    path('', views.ChannelListCreate.as_view(), name="list_create_channel"),
    path('<str:pk>/', views.ChannelRUD.as_view(),
         name="retrive_update_delete_channel")
]
