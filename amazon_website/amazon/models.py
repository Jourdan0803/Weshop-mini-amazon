from django.db import models
from django.core.validators import EmailValidator, MinLengthValidator
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

class Saler(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='Please enter your shop\'s name', max_length=32)

class Products(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='Please enter product name', max_length=32)
    description = models.TextField(verbose_name='Please enter the description for the product')
    types = models.TextField(verbose_name='Please enter the type of product', default="")
    price = models.FloatField(verbose_name='Please enter the price of product', default=0)
    stock = models.IntegerField(verbose_name='Please enter the stock of product')
    image = models.ImageField(upload_to='user_images',verbose_name='Please upload an image for your product', blank=True)
    saler = models.ForeignKey(Saler, on_delete=models.CASCADE)
    warehouse_id = models.IntegerField()
    uploading = models.IntegerField(default=1)

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='Please enter your name', max_length=32, unique=True)
    password = models.CharField(verbose_name='Please enter your password', max_length=300, validators=[MinLengthValidator(8)])
    email = models.CharField(verbose_name='Please enter your email', max_length=32, validators=[EmailValidator()])
    address_x = models.IntegerField(default = 0)
    address_y = models.IntegerField(default = 0)
    payment = models.IntegerField(verbose_name='Please enter your default credit card for payment', default="000")
    is_saler = models.IntegerField(default = 0)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

class Orders(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(default="packing", verbose_name='The status of your order', max_length=32)
    payment = models.IntegerField(verbose_name='The way to pay')
    dest_x = models.IntegerField()
    dest_y = models.IntegerField()
    price = models.FloatField(verbose_name='The price for each',default=0)
    UPS_account = models.CharField(default="None", max_length=32)

class OrderDetails(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE, verbose_name='Order Number')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name='Product you bought')
    quantity = models.IntegerField(verbose_name='The number of product you bought')

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    user_id= models.ForeignKey(Customer, on_delete=models.CASCADE)
    product_name= models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField()

class WareHouse(models.Model):
    id = models.AutoField(primary_key=True)
    x = models.IntegerField()
    y = models.IntegerField()