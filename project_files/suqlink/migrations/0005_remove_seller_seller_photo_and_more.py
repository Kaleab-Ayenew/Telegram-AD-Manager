# Generated by Django 4.1.10 on 2023-07-27 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suqlink', '0004_temporarysellerdata_vcode_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seller',
            name='seller_photo',
        ),
        migrations.AlterField(
            model_name='withdrawrequest',
            name='chapa_webhook_data',
            field=models.TextField(blank=True, null=True),
        ),
    ]