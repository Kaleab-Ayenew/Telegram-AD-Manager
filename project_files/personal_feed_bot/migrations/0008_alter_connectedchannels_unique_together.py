# Generated by Django 4.1.7 on 2023-05-15 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('personal_feed_bot', '0007_remove_feedchannel_id_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='connectedchannels',
            unique_together={('owner_user', 'channel_username', 'feed_channel')},
        ),
    ]