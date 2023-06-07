"""tg_ad_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/', include('accounts.urls')),
    # path('channels/', include('channels.urls')),
    # path('main/', include('main.urls')),
    # path('bot-webhook/', include('bot_webhooks.urls')),
    path('chapa/', include('chapa.urls')),
    path('personal-feed-bot/', include('personal_feed_bot.urls')),
    path('ecom_full/', include('ecom_full.urls')),
    # path('proposal-writer-bot/', include('proposal_writer.urls')),
    path('social-manager/', include('social_manager.urls')),
    path('link/', include('link_shortner.urls')),
    # path('neva-bot/', include('neva_bot.urls')),
    path('black-storm-sub-bot/', include('bot_subscription.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
