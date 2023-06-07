from django.contrib import admin
from .models import FeedgramSubscription, FeedgramFeature
# Register your models here.
admin.site.register(FeedgramSubscription)
admin.site.register(FeedgramFeature)
