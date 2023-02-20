# Generated by Django 4.1.7 on 2023-02-17 17:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('channels', '0003_alter_telegramchannel_ch_username'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('post_content', models.TextField()),
                ('post_image_id', models.CharField(max_length=200, null=True)),
                ('post_buttons', models.JSONField(null=True)),
                ('schedules', models.JSONField()),
                ('destination_channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='channels.telegramchannel')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
