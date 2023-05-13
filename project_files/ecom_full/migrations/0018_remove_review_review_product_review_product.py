# Generated by Django 4.1.7 on 2023-05-10 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecom_full', '0017_remove_review_product_review_review_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='review_product',
        ),
        migrations.AddField(
            model_name='review',
            name='product',
            field=models.ForeignKey(default='ref', on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='ecom_full.product'),
            preserve_default=False,
        ),
    ]
