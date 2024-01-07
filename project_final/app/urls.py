
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
    path('note/<str:date>/',note,name='note'),
    path('show_note/<str:date>/',show_note,name='show-note'),


] 
