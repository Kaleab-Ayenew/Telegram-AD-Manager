# Generated by Django 4.1.7 on 2023-06-13 14:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialManagerUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TelegramData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manager_bot_token', models.CharField(max_length=150)),
                ('channel_username', models.CharField(max_length=100)),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='telegram_data', to='social_manager.socialmanageruser')),
            ],
        ),
        migrations.CreateModel(
            name='FacebookData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fb_user_id', models.CharField(max_length=20)),
                ('user_access_token', models.CharField(max_length=350)),
                ('uat_exp_date', models.DateTimeField()),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='facebook_data', to='social_manager.socialmanageruser')),
            ],
        ),
    ]
