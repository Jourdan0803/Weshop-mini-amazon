from django.shortcuts import render,redirect
from django import forms
# Create your views here.
from django.http import HttpResponse
from amazon import models, apps
from django.db.models import Func
from django.core.mail import send_mail
from django.conf import settings
import logging
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate,login
from django.db.models import Q
import socket
import json
import os
# from apps import global_client_socket



class CustomerRegistrationForm(forms.ModelForm):
    class Meta:
        model =  models.Customer
        fields = ['name', 'password', 'email']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    def clean_username(self):
        name = self.cleaned_data.get('name')
        if models.Customer.objects.filter(name=name).exists():
            raise ValidationError("This username is already taken.")
        return name
    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return pwd

    def clean_email(self):
        email = self.cleaned_data['email']
        if models.Customer.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'usernameInput'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'exampleInputPassword1'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not models.Customer.objects.filter(name=username).exists():
            raise ValidationError("Username does not exist")
        else:
            user = models.Customer.objects.filter(name=username).first()
            self.user = user
            return username
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise ValidationError("password incorrect")
        return password
   

class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Products
        fields = ['name', 'description', 'types', 'price', 'stock', 'image','warehouse_id']

class CheckForm(forms.ModelForm):
    class Meta:
        model = models.Orders
        fields = ['payment', 'dest_x', 'dest_y']

def index(request):
    return render(request,"cart.html")
# Create your views here.

# for customer
def signin_check(func):
    def wrapper():
        # TBD
        func()
    return wrapper

# for saler
def saler_signin_check(func):
    def wrapper():
        # TBD
        func()
    return wrapper

def get_obj_Customer(request):
    info = request.session.get("info")
    userid = info['id']
    obj = models.Customer.objects.filter(id = userid).first()
    return obj
def get_obj_name(request):
    info = request.session.get("info")
    if not info:
        username = "hi!log in or sign up"
    else:
        ob = get_obj_Customer(request)
        username = ob.name
    return username
# jump back to signin/signup
# def jumpback_customer(request):
#   if 
#   return redirect("/customer/signin")

def get_obj_Saler(request,userid):
    obj = models.Saler.objects.filter(id = userid).first()
    return obj

# jump back to signin/signup
# def jumpback_saler(request):
#   if 
#   return redirect("/saler/signin")


# home page
# def home(request):

# select saler/costumer
def select(request):
    if request.method == "GET":
        return render(request, "/home/select")
    if request.method == "POST":
        if 'saler' in request.POST:
            return redirect("/saler/signin")
        return redirect("/costumer/signin")

def signup(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.clean_username()
            pwd = form.clean_password()
            email = form.clean_email()
            user = models.Customer.objects.create(name = user, email = email)
            user.set_password(pwd)
            return redirect('/login')  # Assume there's a home view
    else:
        form = CustomerRegistrationForm()
    return render(request,"signup.html", {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            request.session["info"] = {'id': user.id, 'name': user.name}
            return redirect('/home')
    else:
        form = LoginForm()

    return render(request, "login.html", {'form': form})


def user_logout(request):
    request.session.clear()
    return redirect("/login")

def user_home(request):
    username = get_obj_name(request)
    # connect2back()
    return render(request,"home.html", {'username':username})

def seller_auth(request):
    ob = get_obj_Customer(request)
    saler = ob.is_saler
    if saler == 0:
        return redirect('/seller/signup')
    return redirect('/seller/home')

def seller_signup(request):
    username = get_obj_name(request)
    ob = get_obj_Customer(request)
    print(ob.name)
    if request.method == 'POST':
        print(request.POST) 
        name = request.POST.get('seller')
        print(name)
        seller = models.Saler.objects.create(name = name)
        ob.is_saler = seller.id
        ob.save()
        return render(request,"seller_home.html", {'username': username})
    return render(request,"seller_signup.html", {'username': username})

def seller_home(request):
    ob = get_obj_Customer(request)
    username = get_obj_name(request)
    seller = ob.is_saler
    if seller == 0:
        return redirect('/seller/signup')
    return render(request,"seller_home.html", {'username': username})


def seller_upload(request):
    user = get_obj_Customer(request)
    username = get_obj_name(request)
    saler = get_obj_Saler(request,user.is_saler)
    if request.method == 'POST':
        types = request.POST.get('warehouse_id')
        print(types)
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            name = request.POST.get('name')
            print(name)
            types = request.POST.get('types')
            num = request.POST.get('stock')
            price = request.POST.get('price')
            wh = request.POST.get('warehouse_id')
            description = request.POST.get('description')
            image = request.FILES['image']
            print(request.FILES)
            # where = '%s/user_images/%s' % (settings.MEDIA_ROOT, image)
            where = os.path.join(settings.MEDIA_ROOT, 'user_images', image.name)
            if not os.path.exists(os.path.dirname(where)):
                print("Creating directory:", os.path.dirname(where))  # Debug print
                os.makedirs(os.path.dirname(where))
            else:
                print("Directory already exists:", os.path.dirname(where)) 
            content = image.chunks()
            with open(where, 'wb') as f:
                for i in content:
                    f.write(i)
            p = models.Products.objects.create(name = name,types = types, description=description, stock = num, price = price, warehouse_id = 1,saler = saler, image = image, uploading = 1)
            # back_socket = connect2back()
            product_details = {
                'id': p.id,
                'method': "buymore",
                'description': p.description,
                'whnum': p.warehouse_id,
                'count': p.stock
            }
            data = json.dumps(product_details).encode()
            apps.global_client_socket.sendall(data)
            return redirect('/seller/home') 
        else:
            return render(request, 'seller_upload.html', {'form': form, 'username': username})
    else:
        form = ProductForm()
    return render(request, 'seller_upload.html', {'form': form, 'username': username})




def product_search(request):
    username = get_obj_name(request)
    query = request.GET.get('q', '')
    if query:
        result = models.Products.objects.filter(
            Q(name__icontains=query) | Q(types__icontains=query) | Q(description__icontains=query)
        )
    else:
        result = models.Products.objects.all()
    # if request.method == "GET":
    #     allset = models.Products.objects.all()
    return render(request, "product_search.html", {'username': username,'allset':result})


def product_detail(request, nid):
    ob = get_obj_Customer(request)
    username = get_obj_name(request)
    if request.method == "GET":  
        obj = models.OrderInfo.objects.filter(id=nid).first() 
        return render(request, "driver_order_info.html", {'username': ob.username, 'ob':ob, 'obj':obj})

# # cart page
# # @signin_check

def add_to_cart(request, product_id):
    product = models.Products.objects.get(id=product_id)
    ob = get_obj_Customer(request)
    exists = models.Cart.objects.filter(user_id=ob, product_name=product).exists()
    if exists:
        cart_item = models.Cart.objects.get(user_id=ob, product_name=product)
        cart_item.quantity += 1
        cart_item.save()
    else:
        models.Cart.objects.create(user_id = ob,product_name = product,quantity = 1)
    return redirect('/cart') 

def cart(request):
    ob = get_obj_Customer(request)
    username = get_obj_name(request)
    if request.method == "GET":  
        allset = models.Cart.objects.filter(user_id = ob)
        print(allset)
        sumPrice = 0
        for i in allset:
            sumPrice += i.quantity*i.product_name.price
        if sumPrice >= 100:
            deliver = 0
        else:
            deliver = 3.99
        total = sumPrice+deliver
        return render(request, "cart.html", {'username': username, 'allset':allset,'sum':sumPrice,'deliver':deliver,'total':total})

def delete_cart(request, product_id):
    product = models.Cart.objects.get(id=product_id)
    product.delete()
    return redirect('/cart') 

def checkout(request):
    ob = get_obj_Customer(request)
    username = get_obj_name(request)
    allset = models.Cart.objects.filter(user_id = ob)
    sumPrice = 0
    for i in allset:
        sumPrice += i.quantity*i.product_name.price
    if sumPrice >= 100:
        deliver = 0
    else:
        deliver = 3.99
    total = sumPrice+deliver
    if request.method == 'POST':
        # types = request.POST.get('warehouse_id')
        # print(types)
        form = CheckForm(request.POST)
        if form.is_valid():
            address_x = request.POST.get('dest_x')
            address_y = request.POST.get('dest_y')
            payment = request.POST.get('payment')
            ups = request.POST.get('ups')
            # create order
            order = models.Orders.objects.create(customer_id = ob, payment = payment, dest_x = address_x, dest_y = address_y,price = total, UPS_account = ups)
            order_details = {
                'whnum': 1,
                'things_list': [],
                'orderid': order.id,
                'method': "topack",
                'ups_account': order.UPS_account,
                'dest_x': order.dest_x,
                'dest_y': order.dest_y
            }
            print("*************")
            print(order_details)
            for item in allset:
                # add cart item to order detail
                models.OrderDetails.objects.create(order_id = order, product_id = item.product_name, quantity = item.quantity)
                # edit product stock
                item.product_name.stock -= item.quantity
                item.product_name.save()
                list_item = {'id': item.product_name.id, 'description': item.product_name.description, 'count': item.quantity}
                order_details['things_list'].append(list_item)
            # delete item from cart
            allset.delete()

            print(order_details)
            data = json.dumps(order_details).encode()
            apps.global_client_socket.sendall(data)
            return redirect('/home') 
        else:
            return render(request, 'checkout.html', {'form': form, 'ob': ob, 'username': username, 'allset': allset,'total':total})
    else:
        form = ProductForm()
    return render(request, 'checkout.html', {'form': form,'ob': ob,'username': username,'allset': allset, 'total':total})



# # order list
# # @signin_check
def order_list(request):
    ob = get_obj_Customer(request)
    username = get_obj_name(request)
    if request.method == "GET":  
        allset = models.Orders.objects.filter(customer_id = ob)
        return render(request, "orders.html", {'username': username, 'allset':allset})


def order_detail(request, order_id):
    order = models.Orders.objects.filter(id = order_id).first()
    allset = models.OrderDetails.objects.filter(order_id = order)
    first = models.OrderDetails.objects.filter(order_id = order).first()
    products = models.Products.objects.filter( types= first.product_id.types)
    print(allset)
    username = get_obj_name(request)
    ob = get_obj_Customer(request)
    return render(request, 'order_detail.html', {'ob': ob,'username': username,'allset': allset,'order':order,'products':products})


# # saler profile page, prodcuct lists
# # @saler_signin_check
def saler_product(request):
    username = get_obj_name(request)
    ob = get_obj_Customer(request)  
    query= models.Products.objects.filter(saler_id = ob.is_saler)
    return render(request, "seller_products.html", {'username': username,'allset':query})


# saler product page-edit
# # @saler_signin_check
