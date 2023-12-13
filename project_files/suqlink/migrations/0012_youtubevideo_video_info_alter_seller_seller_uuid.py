# Generated by Django 4.1.10 on 2023-12-06 20:06

from django.db import migrations, models
import suqlink.models


class Migration(migrations.Migration):

    dependencies = [
        ('suqlink', '0011_seller_seller_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='youtubevideo',
            name='video_info',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='seller',
            name='seller_uuid',
            field=models.UUIDField(default=suqlink.models.get_seller_id),
        ),
    ]
