from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.CreateListPost.as_view(), name='create_list_post_url'),
    path('posts/<uuid:unique_id>', views.PostRUD.as_view(), name='post_rud_url'),
]
