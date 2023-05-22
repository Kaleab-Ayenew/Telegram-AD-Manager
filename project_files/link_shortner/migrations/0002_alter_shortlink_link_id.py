# Generated by Django 4.1.7 on 2023-05-22 16:02

from django.db import migrations, models
import link_shortner.models


class Migration(migrations.Migration):

    dependencies = [
        ('link_shortner', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shortlink',
            name='link_id',
            field=models.CharField(default=link_shortner.models.get_link_id, editable=False, max_length=8, primary_key=True, serialize=False),
        ),
    ]
