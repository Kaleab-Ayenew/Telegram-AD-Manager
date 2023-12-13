# Generated by Django 4.1.10 on 2023-11-28 11:18

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import suqlink.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('suqlink', '0009_auto_20230921_2114'),
    ]

    operations = [
        migrations.CreateModel(
            name='YoutubeVideoClient',
            fields=[
                ('video_client_username', models.EmailField(max_length=100, primary_key=True, serialize=False)),
                ('video_client_timestamp', models.DateTimeField(auto_now_add=True)),
                ('main_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='video_client', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='YoutubeVideo',
            fields=[
                ('platform_id', models.CharField(default=suqlink.models.get_templink_id, editable=False, max_length=10, primary_key=True, serialize=False)),
                ('video_id', models.CharField(max_length=15)),
                ('video_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000)])),
                ('video_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='youtube_videos', to='suqlink.seller')),
            ],
        ),
        migrations.CreateModel(
            name='YoutubeSale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sale_timestamp', models.DateTimeField(auto_now_add=True)),
                ('chapa_transaction_ref', models.UUIDField(null=True, unique=True)),
                ('completed', models.BooleanField(default=False)),
                ('sale_price', models.DecimalField(decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000)])),
                ('sold_video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='suqlink.youtubevideo')),
                ('video_buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_purchases', to='suqlink.youtubevideoclient')),
            ],
        ),
    ]