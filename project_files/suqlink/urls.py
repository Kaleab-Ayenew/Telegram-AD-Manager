from django.urls import path
from . import views
urlpatterns = [
    path("register/", views.create_tempseller),
    path("email/verify/<uuid:temp_data_uuid>/", views.verify_email),
    path("login/", views.login_view),
    path("products/new/", views.create_product),
    path("products/list/", views.list_products),
    path("products/detail/<str:product_id>/",
         views.ProductRetriveView.as_view()),
    path("products/<str:product_id>/", views.ProductRUD.as_view()),
    path("payment/get-payment-link/<str:product_id>/", views.get_payment_link),
    path("payment/verify/<uuid:transaction_ref>/", views.chapa_callback_verify),
    path("download/<str:link_id>", views.product_download_handler),
    path("payment/withdraw/", views.withdraw_to_bank),
    path("webhook/", views.chapa_event_webhook),
    path("stats/", views.get_full_stats),
    path("bank-list/", views.get_chapa_bank_list),
]
