# Generated by Django 4.1.7 on 2023-05-15 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecom_full', '0022_remove_order_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('chapa', 'chapa'), ('cash', 'cash')], default='cash', max_length=30),
        ),
    ]
