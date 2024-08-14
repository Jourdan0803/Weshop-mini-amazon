"""
URL configuration for amazon_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from amazon import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.user_home, name='home'),
    path('index/', views.index),
    path('signup/', views.signup),
    path('login/', views.user_login),
    path('home/', views.user_home),
    path("logout", views.user_logout),
    path("products", views.product_search, name='product_search'),
    path("seller/auth", views.seller_auth),
    path("seller/signup", views.seller_signup),
    path("seller/home", views.seller_home),
    path("seller/upload", views.seller_upload),
    path('add_cart/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('delete_cart/<int:product_id>/', views.delete_cart, name='delete_cart'),
    path('cart',views.cart),
    path('checkout', views.checkout),
    path('orders', views.order_list),
    path('order/<int:order_id>/info', views.order_detail),
    path('seller/products', views.saler_product),
    
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)