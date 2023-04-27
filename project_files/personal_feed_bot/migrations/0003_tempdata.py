# Generated by Django 4.1.7 on 2023-04-27 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal_feed_bot', '0002_botuser_feed_channel_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_user', models.CharField(max_length=50, unique=True)),
                ('active_question', models.IntegerField(default=0)),
            ],
        ),
    ]
