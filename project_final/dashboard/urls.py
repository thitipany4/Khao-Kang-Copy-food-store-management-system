from django.urls import path,include
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('',home),
    path('download/', download_excel, name='download_excel'),

] 

