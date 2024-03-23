from django.urls import path,include
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('',see_all_data,name='see_all_data'),
    path('SeeMonth/',see_month_data,name='see_month_data'),
    path('SeeMonth/filter/',see_month_data,name='see_month_data_filter'),
    path('SeeQuarter/',see_quarter_data,name='see_quarter_data'),
    path('SeeQuarter/filter/',see_quarter_data,name='see_quarter_data_filter'),

    path('download/', download_excel, name='download_excel'),
    path('download/select_range/', download_range, name='download_excel_range'),
    path('reasonAndtime/',reason_time,name='reason_time'),
    path('delete_reason/<str:id>/',delete_reason,name='delete_reason'),
    path('delete_time/<str:id>/',delete_time,name='delete_time'),
    path('add_reason/',save_reason,name='save_reason'),
    path('add_time/',save_time,name='save_time'),





] 

