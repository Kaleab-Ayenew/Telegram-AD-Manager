# Generated by Django 4.1.10 on 2023-12-06 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suqlink', '0012_youtubevideo_video_info_alter_seller_seller_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='youtubevideo',
            name='video_id',
            field=models.CharField(max_length=70),
        ),
    ]