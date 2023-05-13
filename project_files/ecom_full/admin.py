from django.contrib import admin
from .models import Product, ProductImage, Review, Discount, Order, EcomAdmin
# Register your models here.


# class ProductAdmin(admin.ModelAdmin):
#     prepopulated_fields = {"slug": ["title"]}


admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Review)
admin.site.register(Discount)
admin.site.register(Order)
admin.site.register(EcomAdmin)
