# Generated by Django 4.1.7 on 2023-05-02 07:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecom_full', '0003_alter_product_oldprice'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productimage',
            old_name='image_file',
            new_name='img',
        ),
    ]