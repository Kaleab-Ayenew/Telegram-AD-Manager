# Generated by Django 4.1.7 on 2023-05-02 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecom_full', '0004_rename_image_file_productimage_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='additional_info',
            field=models.JSONField(null=True),
        ),
    ]
