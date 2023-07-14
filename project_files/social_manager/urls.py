from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.post_action),
    path('auth/', views.login_view),
    path('sign-up/', views.sign_up_view),
    path('fb-create/', views.create_fb_data),
    path('fb-update/', views.update_fb_data),
    path('get-fb-pages/', views.get_fb_pages),
    path('get-ig-pages/', views.get_ig_pages),
    path('get-tg-pages/', views.get_tg_pages),
]
