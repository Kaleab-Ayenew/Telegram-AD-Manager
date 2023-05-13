from django.urls import path
from . import views

urlpatterns = [
    path('static/product.json', views.ProductListView.as_view(),
         name="product-list-url"),
    path('static/products/new/', views.ProductCreateView.as_view(),
         name="product-create-url"),
    path("static/products/<slug:slug>/", views.ProductRUDView.as_view()),
    path("static/products/<slug:slug>/image/", views.ImageCreateView.as_view()),
    path("static/orders/", views.OrderListView.as_view()),
    path("static/orders/new/", views.OrderCreateView.as_view()),
    path("static/get-sales-data/", views.get_sales_data),
    path("auth/login/", views.login_view),
]
