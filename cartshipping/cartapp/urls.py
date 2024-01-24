from django.contrib import admin
from django.urls import include, path
from .views import *

urlpatterns = [
    path('',home,name='home'),
    path('add/', add_product, name='add_product'),
    path('list/', product_list, name='product_list'), 
    path('list2/', product_list2, name='product_list2'), 
    path('create_cart/', create_cart, name='create_cart'),
    path('delete_cart/', delete_cart, name='delete_cart'),
    path('add-to-cart/<str:type>/', add_to_cart, name='add_to_cart'),
    path('view-cart/', view_cart, name='view_cart'),
    path('order-confirmation/<int:order_id>/', order_confirmation, name='order_confirmation'),  # Update this line
    path('checkout/', checkout, name='checkout'), 
    path('place-order/', place_order, name='place_order'), 
    path('order-history/', order_history, name='order_history'),
    path('confirm_order/<int:order_id>/', confirm_order, name='confirm_order'),
    path('cart/delete/<int:product_id>/', delete_from_cart, name='delete_from_cart'),
]
