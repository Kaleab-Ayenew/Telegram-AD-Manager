# Generated by Django 4.1.7 on 2023-07-20 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suqlink', '0002_alter_sale_sold_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_short_description',
            field=models.CharField(default='Short description', max_length=300),
            preserve_default=False,
        ),
    ]
