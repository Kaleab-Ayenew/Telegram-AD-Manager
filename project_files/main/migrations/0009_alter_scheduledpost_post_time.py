# Generated by Django 4.1.7 on 2023-04-21 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_alter_scheduledpost_post_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduledpost',
            name='post_time',
            field=models.DateTimeField(),
        ),
    ]
