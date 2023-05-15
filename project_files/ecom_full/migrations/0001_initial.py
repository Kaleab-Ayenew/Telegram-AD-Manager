# Generated by Django 4.1.7 on 2023-05-02 04:22

from django.db import migrations, models
import django.db.models.deletion
import ecom_full.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=200)),
                ('moreLove', models.BooleanField()),
                ('price', models.IntegerField()),
                ('oldPrice', models.IntegerField(null=True)),
                ('desc', models.TextField()),
                ('totalSell', models.IntegerField(default=0)),
                ('condition', models.CharField(choices=[('brand new', 'brand new'), ('slightly used', 'slightly used'), ('used', 'used')], default='brand new', max_length=15)),
                ('vendor', models.CharField(default='Neva Computers', max_length=25)),
                ('color', models.CharField(max_length=15)),
                ('brand', models.CharField(max_length=20)),
                ('category', models.CharField(max_length=50)),
                ('featured', models.BooleanField()),
                ('trending', models.BooleanField()),
                ('variations', models.JSONField(null=True)),
                ('weight', models.IntegerField()),
                ('tags', models.JSONField(null=True)),
                ('size', models.CharField(choices=[('s', 's'), ('m', 'm'), ('l', 'l')], default='m', max_length=1)),
                ('stock', models.IntegerField()),
                ('rating', models.IntegerField()),
                ('ratingScore', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_text', models.TextField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='ecom_full.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_file', models.ImageField(max_length=150, upload_to=ecom_full.models.get_image_path)),
                ('parent_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='ecom_full.product')),
            ],
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage', models.IntegerField()),
                ('expireDate', models.DateField(null=True)),
                ('isActive', models.BooleanField(default=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discount', to='ecom_full.product', unique=True)),
            ],
        ),
    ]