# Generated by Django 4.1.7 on 2023-05-10 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecom_full', '0008_alter_product_unique_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(editable=False, max_length=200, unique=True),
        ),
    ]