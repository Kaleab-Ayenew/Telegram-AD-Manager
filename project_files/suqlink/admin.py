from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.ChapaBank)
admin.site.register(models.TempDownloadLink)
admin.site.register(models.TemporarySellerData)
admin.site.register(models.Sale)
admin.site.register(models.Product)
admin.site.register(models.Seller)
admin.site.register(models.WithdrawRequest)
