
from django.urls import path,include

from app.views import *

urlpatterns = [
    path('',home, name='home'),
    path('create/',create,name='create'),
    path('managefood/',managefood,name='managefood'),
    path('managefood/<str:date>/',managefood,name='managefood_add'),
    path('select_date/',select_date,name='select_date'),
    path('history_sale/',select_date,name='select_date'),
    path('clear_food/',clearfood,name='clear_food'),
    path('updatefood/<int:id>/',updatefood,name='updatefood'),
    path('delete/<int:id>/',delete, name='delete-food'),
    path('search/',search,name='search'),
    path('foodview/<int:id>/',foodview,name='foodview'),
    path('foodview/<int:id>/<str:target>/',foodview,name='sort_food'),
    path('review/<int:id>/',reviewfood,name='review'),
    path('login/',login,name='custom_login'),
    path('line-login/', line_login, name='line'),
    path('logout/', logout, name='logout'),
    path('login/callback/',line_callback,name='line_ callback'),
    path('about_us/',about_us,name='about-us'),
    path('profile/<str:username>/',profile,name='profile'),
    path('calendar/',calendar,name='calendar'),
    path('calendar/<str:date>/<str:mark>/',calendar,name='calendar-date'),
    path('note/<str:date>/<str:type>/',note,name='note'),
    path('note/<str:date>/<str:type>/<str:filter>/',note,name='note'),
    path('delete_note/<str:date>/<str:type>/<int:id>/',delete_note,name='delete_note'),
    path('show_note/<str:date>/',show_note,name='show-note'),
    path('show_note/<str:date>/<str:type>/',show_note,name='show-note'),
    

    path('create_cart/', create_cart, name='create_cart'),
    path('view-cart/', view_cart, name='view_cart'),
    path('delete_cart/<str:code>/', delete_cart, name='delete_cart'),
    path('add-to-cart/<str:type>/', add_to_cart, name='add_to_cart'),
    path('add-to-cart/<str:type>/<str:modify>/', add_to_cart, name='add_to_cart'),
    path('shopping_food_type1/', shopping_food_type1, name='shopping_food1'),
    path('modify_cart1/<str:ref_code>/', modify_cart1, name='modify_cart1'),
    path('shopping_food_type2/', shopping_food_type2, name='shopping_food2'), 
    path('modify_cart2/<int:id>/', modify_cart2, name='modify_cart2'),
    path('cart/delete/<int:product_id>/<str:type>/', delete_from_cart, name='delete_from_cart'),
    path('checkout/', checkout, name='checkout'), 
    path('order_confirm/<str:ref_code>/', order_confirmation, name='order_confirm'),
    path('confirm_order/', confirm_order, name='confirm_order'),
    path('confirm_order/<str:code>/<str:status>/', confirm_order, name='confirm_order'), 
    path('history_confirm_order/',history_confirm_order,name='history_confirm_order'),
    path('history_confirm_order/<str:date>/',history_confirm_order,name='confirm_order_admin'),
    path('history_confirm_order/<str:date>/<str:filter>/',history_confirm_order,name='confirm_order_admin'),
    path('my_order/',my_order,name='my_order'),
    path('history_order/',my_history,name='my_history'),
    path('history_order/<str:filter>/',my_history,name='my_history'),



] 
