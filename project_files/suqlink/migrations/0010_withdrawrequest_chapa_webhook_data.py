# Generated by Django 4.1.7 on 2023-07-15 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suqlink', '0009_alter_withdrawrequest_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdrawrequest',
            name='chapa_webhook_data',
            field=models.TextField(null=True),
        ),
    ]