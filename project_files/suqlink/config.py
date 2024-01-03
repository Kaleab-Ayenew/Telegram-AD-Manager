from django.conf import settings

CHAPA_API_VERSION = "v1"
CHAPA_SECRET_TOKEN = settings.CHAPA_SECRET_TOKEN
CHARGE_PERCENT = 5
YOUTUBE_CHARGE_PERCENT = 10
CHAPA_WEBHOOK_SECRET = settings.CHAPA_WEBHOOK_SECRET
SENDGRID_API_KEY = settings.SENDGRID_API_KEY
SUQLINK_PRODUCT_DOMAIN = "https://p.suqlink.com/"
YT_VIDEO_DOMAIN = "http://localhost:3000/" if not settings.PROD else "https://yt.suqlink.com/"
ADMIN_SELLER_USERNAME = "kalish"
