# Generated by Django 4.1.7 on 2023-07-15 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suqlink', '0007_alter_withdrawrequest_withdraw_reference'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdrawrequest',
            name='status',
            field=models.CharField(default='pending', max_length=10),
        ),
    ]
