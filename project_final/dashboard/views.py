from django.shortcuts import render
from django_plotly_dash.views import add_to_session
from flask import redirect
from app.models import *
from .app import app
from django.http import HttpResponse
import pandas as pd
from io import BytesIO
def home(req):
    add_to_session(req,app)
    income = 0
    expenses = 0
    pre_income = 0
    pre_expenses = 0
    current = datetime.now().date()

    current_year = current.year
    current_month = current.month
    current_month = str(current_month).zfill(2) 

    previous_month = current.month - 1
    if previous_month == 0:
        previous_month = 12  
        current_year -= 1  
    previous_month_str = str(previous_month).zfill(2) #ไว้ทำให้เป็นตัวเลข 2 ตำแหน่ง
    previous_transactions = Transaction.objects.filter(date__year=current_year, date__month=previous_month_str)
    transactions = Transaction.objects.filter(date__year=current_year,date__month=current_month)

    date_filter = f'{current_year}-{current_month}'
    pre_date_filter = f'{current_year}-{previous_month_str}'

    sale = Order.objects.filter(completed='completed',created_at__contains=date_filter)
    order = Order.objects.filter(confirm='cancel',created_at__contains=date_filter)

    pre_sale = Order.objects.filter(completed='completed',created_at__contains=pre_date_filter)
    pre_order = Order.objects.filter(confirm='cancel',created_at__contains=pre_date_filter)
    print(sale)
    print(pre_sale)

    for t in transactions:
        if t.transaction_type == 'income':
            income += t.total_price
        elif t.transaction_type == 'expenses':
            expenses += t.total_price

    for t in previous_transactions:
        if t.transaction_type == 'income':
            pre_income += t.total_price
        elif t.transaction_type == 'expenses':
            pre_expenses += t.total_price
            
    income_compare = int(((income - pre_income) / pre_income) * 100)
    expenses_compare = int(((expenses - pre_expenses) / pre_expenses) * 100)

    success = len(sale)
    cancel = len(order)
    pre_success=len(pre_sale)
    pre_cancel = len(pre_order)

    success_compare = int(((success - pre_success) / pre_success) * 100)
    cancel_compare = int(((cancel - pre_cancel) / pre_cancel) * 100)

    context = {
        'app':app,
        'income':income,
        'expenses':expenses,
        'income_compare':income_compare,
        'expenses_compare':expenses_compare,
        'success':success,
        'cancel':cancel,
        'success_compare':success_compare,
        'cancel_compare':cancel_compare,
    }
    return render(req,'dashboard/home.html',context)

def download_excel(req):
    transactions = Transaction.objects.filter(transaction_type__in=['income', 'expenses']).order_by('date')
    print(transactions)
    # Organize data
    data = []
    current_date = None
    income = 0
    expenses = 0
    for transaction in transactions:
        current_date = transaction.date
        income = 0
        expenses = 0
        if transaction.transaction_type == 'income':
            income += transaction.price
            type_str = 'รายรับ'
        elif transaction.transaction_type == 'expenses':
            expenses += transaction.price
            type_str = 'รายจ่าย'

        formatted_date = current_date.strftime('%Y/%m/%d')
        data.append({'วันที่': formatted_date,'ชื่อ':transaction.name,'จำนวน':transaction.amount ,'ราคา':transaction.price,'ราคารวม':transaction.total_price
                     ,'ประเภท': type_str})
        

    
    df = pd.DataFrame(data)
    print(df)
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    
    # Create HTTP response with Excel file content
    response = HttpResponse(excel_buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Report_Finacial.xlsx"'
    
    return response