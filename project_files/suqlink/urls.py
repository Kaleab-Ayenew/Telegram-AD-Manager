from django.urls import path
from . import views
urlpatterns = [
    path("register/", views.create_tempseller),
    path("email/verify/<uuid:temp_data_uuid>/", views.verify_email),
    path("email/resend/<uuid:temp_data_uuid>/", views.resend_email),
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
    # Video Selling Auth
    path("yvideos/c/register", views.register_video_client),
    path("yvideos/c/login", views.login_video_client),
    path("yvideos/c/me", views.get_client_info),

    # Video Selling Endpoints
    path("yvideos/create/", views.create_youtube_video),
    path("yvideos/videos", views.AnonListVideos.as_view()),
    path("yvideos/videos/<str:platform_id>",
         views.AnonSingleVideoData.as_view()),

    path("yvideos/s/videos/", views.SellerListVideos.as_view()),
    path("yvideos/s/videos/<str:platform_id>", views.SellerVideoRUD.as_view()),
    #     path("yvideos/c/videos", views.ClientListVideos.as_view()),
    #     path("yvideos/c/videos/<str:platform_id>",
    #          views.ClientSingleVideoData.as_view()),
    path("yvideos/c/videos/purchased", views.ClientPurchasedVideos.as_view()),

    path("yvideos/c/videos/purchased/<str:platform_id>",
         views.ClientPurchasedVideoData.as_view()),

    path("yvideos/c/payment/get-payment-link/<str:platform_id>",
         views.get_video_payment_link),
    path("yvideos/c/payment/verify/<str:transaction_ref>",
         views.video_chapa_callback_verify),
    # Video Stats
    path("yvideos/s/stats/",
         views.video_get_full_stats),

]
