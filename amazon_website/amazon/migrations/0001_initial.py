# Generated by Django 4.2.9 on 2024-04-20 17:42

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='Please enter your name')),
                ('password', models.CharField(max_length=300, validators=[django.core.validators.MinLengthValidator(8)], verbose_name='Please enter your password')),
                ('email', models.CharField(max_length=32, validators=[django.core.validators.EmailValidator()], verbose_name='Please enter your email')),
                ('address_x', models.IntegerField(default=0)),
                ('address_y', models.IntegerField(default=0)),
                ('payment', models.IntegerField(default='000', verbose_name='Please enter your default credit card for payment')),
                ('is_saler', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Saler',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32, verbose_name="Please enter your shop's name")),
            ],
        ),
        migrations.CreateModel(
            name='WareHouse',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32, verbose_name='Please enter product name')),
                ('description', models.TextField(verbose_name='Please enter the description for the product')),
                ('types', models.TextField(default='', verbose_name='Please enter the type of product')),
                ('price', models.FloatField(default=0, verbose_name='Please enter the price of product')),
                ('stock', models.IntegerField(verbose_name='Please enter the stock of product')),
                ('image', models.ImageField(blank=True, upload_to='', verbose_name='Please upload an image for your product')),
                ('warehouse_id', models.IntegerField()),
                ('saler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amazon.saler')),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(default='ordered', max_length=32, verbose_name='The status of your order')),
                ('payment', models.IntegerField(verbose_name='The way to pay')),
                ('dest_x', models.IntegerField()),
                ('dest_y', models.IntegerField()),
                ('customer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amazon.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('product_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amazon.products')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amazon.customer')),
            ],
        ),
    ]
