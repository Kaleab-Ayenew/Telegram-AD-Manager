# Generated by Django 4.1.7 on 2023-05-10 20:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecom_full', '0013_remove_productimage_parent_product_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discount',
            name='product',
        ),
        migrations.AddField(
            model_name='discount',
            name='product_target',
            field=models.OneToOneField(default='Shit', on_delete=django.db.models.deletion.CASCADE, related_name='discount', to='ecom_full.product'),
            preserve_default=False,
        ),
    ]
