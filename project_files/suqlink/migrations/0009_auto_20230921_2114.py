# Generated by Django 4.1.10 on 2023-09-21 18:14

from django.db import migrations


def set_default_sale_price(apps, schema_editor):
    Sale = apps.get_model('suqlink', 'Sale')
    for sale in Sale.objects.filter(sale_price__isnull=True):
        sale.sale_price = sale.sold_product.product_price
        sale.save()


class Migration(migrations.Migration):

    dependencies = [
        ('suqlink', '0007_sale_sale_price'),
    ]

    operations = [
        migrations.RunPython(set_default_sale_price),
    ]
