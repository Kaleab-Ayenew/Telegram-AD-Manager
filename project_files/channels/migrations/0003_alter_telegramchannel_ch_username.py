# Generated by Django 4.1.7 on 2023-02-17 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0002_telegramchannel_id_alter_telegramchannel_ch_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramchannel',
            name='ch_username',
            field=models.CharField(max_length=150, unique=True),
        ),
    ]
