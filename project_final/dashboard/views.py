from django.shortcuts import render,redirect
from django_plotly_dash.views import add_to_session
from app.models import *
from app.getdate import getdate
from .dashboards import *
from django.http import HttpResponse
import pandas as pd
from io import BytesIO
import calendar
from .quarter_get_data import *
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


# def select_month_dash(req):
#     if req.method == 'POST':
#         month = req.POST.get('move_to_month')
#         print(month)

#         test_tra = Transaction.objects.filter(date__contains=month)
#         cancel_test = Order.objects.filter(confirm='cancel',created_at__contains=month)
#         com_test = Order.objects.filter(completed='completed',created_at__contains=month)
#         print('test get date',test_tra)
#         print('test get date2',cancel_test)
#         print('test get date3',com_test)
#     return redirect('see_all_data')
def get_all_data():
    income = 0
    expenses = 0

    current_year = date.year
    current_month = date.month
    current_month = str(current_month).zfill(2) 

    print(current_year,current_month)

    
    transactions = Transaction.objects.all()

    sale = Order.objects.filter(completed='completed')
    cancel = Order.objects.filter(confirm='cancel')
    print(sale)

    for t in transactions:
        if t.transaction_type == 'income':
            income += t.total_price
        elif t.transaction_type == 'expenses':
            expenses += t.total_price
            
    success = len(sale)
    cancel = len(cancel)

    return income,expenses,success,cancel

def get_month_data(date):
    income = 0
    expenses = 0
    pre_income = 0
    pre_expenses = 0

    current_year = date.year
    current_month = date.month

    current_month = str(current_month).zfill(2) 

    previous_month = date.month - 1
    pre_current_year = current_year
    if previous_month == 0:
        previous_month = 12  
        pre_current_year = current_year - 1 
    previous_month_str = str(previous_month).zfill(2) #ไว้ทำให้เป็นตัวเลข 2 ตำแหน่ง

    date_filter = f'{current_year}-{current_month}'
    pre_date_filter = f'{pre_current_year}-{previous_month_str}'
    print(date_filter,'date_filter',pre_date_filter,'pre_date_filter')
    previous_transactions = Transaction.objects.filter(date__contains=pre_date_filter)
    transactions = Transaction.objects.filter(date__contains=date_filter)

    print(transactions,'transactions',previous_transactions,'previous_transactions')
    sale = Order.objects.filter(completed='completed',created_at__contains=date_filter)
    cancel = Order.objects.filter(confirm='cancel',created_at__contains=date_filter)

    pre_sale = Order.objects.filter(completed='completed',created_at__contains=pre_date_filter)
    pre_cancel = Order.objects.filter(confirm='cancel',created_at__contains=pre_date_filter)
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

    success = len(sale)
    cancel = len(cancel)
    pre_success =len(pre_sale)
    pre_cancel = len(pre_cancel)
   
    if not pre_sale and not pre_cancel and not transactions and not previous_transactions:
        income_compare ='N/A'
        expenses_compare='N/A'
        pre_success='N/A'
        pre_cancel = 'N/A'
        success_compare = 'N/A'
        cancel_compare = 'N/A'
    else:
        if pre_income == 0:
            income_compare = 'N/A'
        else:
            income_compare = int(((income - pre_income) / pre_income) * 100)
            
        if pre_expenses == 0:
            expenses_compare = 'N/A'
        else:
            expenses_compare = int(((expenses - pre_expenses) / pre_expenses) * 100)
            
        if pre_success == 0:
            success_compare = 'N/A'
        else:
            success_compare = int(((success - pre_success) / pre_success) * 100)
            
        if pre_cancel == 0:
            cancel_compare = 'N/A'
        else:
            cancel_compare = int(((cancel - pre_cancel) / pre_cancel) * 100)

    return income,expenses,income_compare,expenses_compare,success,cancel,success_compare,cancel_compare 

def get_quarter_data(quarter,year):
    income = 0
    expenses = 0
    pre_income = 0
    pre_expenses = 0

    if quarter == 1 :
        pre_year = year -1
        previous_quarter = 1
    else:
        previous_quarter = 1
        pre_year = year

    len_quarter = get_month_dates(year,quarter)
    pre_len_quarter = get_month_dates(pre_year,previous_quarter)


    previous_transactions = Transaction.objects.filter(date__range=(pre_len_quarter))
    transactions = Transaction.objects.filter(date__range=(len_quarter))

    sale = Order.objects.filter(completed='completed',created_at__range=(len_quarter))
    cancel = Order.objects.filter(confirm='cancel',created_at__range=(len_quarter))

    pre_sale = Order.objects.filter(completed='completed',created_at__range=(pre_len_quarter))
    pre_cancel = Order.objects.filter(confirm='cancel',created_at__range=(pre_len_quarter))


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

    success = len(sale)
    cancel = len(cancel)
    pre_success =len(pre_sale)
    pre_cancel = len(pre_cancel)
   
    if not pre_sale and not pre_cancel and not transactions and not previous_transactions:
        income_compare ='N/A'
        expenses_compare='N/A'
        pre_success='N/A'
        pre_cancel = 'N/A'
        success_compare = 'N/A'
        cancel_compare = 'N/A'
    else:
        if pre_income == 0:
            income_compare = 'N/A'
        else:
            income_compare = int(((income - pre_income) / pre_income) * 100)
            
        if pre_expenses == 0:
            expenses_compare = 'N/A'
        else:
            expenses_compare = int(((expenses - pre_expenses) / pre_expenses) * 100)
            
        if pre_success == 0:
            success_compare = 'N/A'
        else:
            success_compare = int(((success - pre_success) / pre_success) * 100)
            
        if pre_cancel == 0:
            cancel_compare = 'N/A'
        else:
            cancel_compare = int(((cancel - pre_cancel) / pre_cancel) * 100)

    return income,expenses,income_compare,expenses_compare,success,cancel,success_compare,cancel_compare 

def call_user(user):
    if user.is_superuser:
        print(user.id)
        member = Member.objects.get(pk=user.id)
        return member
    else:
        return None
    
def is_superuser(user):
    return user.is_authenticated and user.is_superuser


@login_required
def see_all_data(req,filter=None):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    show_text = 'ข้อมูลทั้งหมด'
    if req.method == 'POST':
        month = req.POST.get('move_to_month')
        print(month)
        current = datetime.now().date()

    else:
        current = datetime.now().date()

    if filter:
        app = call_all()
        add_to_session(req,app)
        print('filter',filter)

    else:
        app = call_all()
        add_to_session(req,app)

    month_data = 'month'
    quater_data = 'quater'

    income,expenses,success,cancel, = get_all_data()
    user = req.user
    user_check = call_user(user)

    context = {
        'app':app,
        'income':income,
        'expenses':expenses,
        'success':success,
        'cancel':cancel,
        'month_data':month_data,
        'quater_data':quater_data,
        'show_text':show_text,
        'user':user_check,
    }
    return render(req,'dashboard/home.html',context)

@login_required
def see_month_data(req):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    show_text = 'ข้อมูลทั้งหมด'
    mark = 'Month'
    if req.method == 'POST':
        select_date = req.POST.get('move_to_month')
        print('month',select_date)

        split = select_date.split('-')
        text_send_tra = f'{split[0]}-{split[1]}-12'
        date = getdate(None,str(text_send_tra))
        date = date.split(' ')
        show_text = f'{date[1]} {date[2]}'

        year, month = map(int, select_date.split("-"))
        all_days = calendar.monthrange(year, month)[1]
        list_day = [day for day in range(1, all_days + 1)]
        month = str(month).zfill(2) 
        app = call_month(select_date,list_day)
        add_to_session(req,app)
        raw_current = f'{split[0]}-{split[1]}'
        current = datetime.strptime(raw_current, "%Y-%m")

    else:
        current = datetime.now().date()
        year_t = current.year
        month_t = current.month

        all_days = calendar.monthrange(year_t, month_t)[1]
        list_day = [day for day in range(1, all_days + 1)]
        if month_t < 10 :
            month_t = f'0{month_t}'
        date = getdate(None,str(current))
        date = date.split(' ')[1:]
        show_text = f'{date[0]} {date[1]}'
        print(date)
        print(show_text)

        print(current.year,current.month,'current year month')
        send_date = str(current).split('-')[0:2]
        send_date = f'{send_date[0]}-{send_date[1]}'
        app = call_month(send_date,list_day)
        add_to_session(req,app)

    month_data = 'month'
    quater_data = 'quater'

    income,expenses,income_compare,expenses_compare,success,cancel,success_compare,cancel_compare = get_month_data(current)
    user = req.user
    user_check = call_user(user)
    context = {
        'income':income,
        'expenses':expenses,
        'income_compare':income_compare,
        'expenses_compare':expenses_compare,
        'success':success,
        'cancel':cancel,
        'success_compare':success_compare,
        'cancel_compare':cancel_compare,
        'month_data':month_data,
        'quater_data':quater_data,
        'show_text':show_text,
        'mark':mark,
        'user':user_check
    }
    return render(req,'dashboard/home.html',context)

@login_required
def see_quarter_data(req):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    show_text = 'ข้อมูลทั้งหมด'
    mark = 'Quarter'
    select_quarter = [1,2,3,4]
    if req.method == 'POST':
        quarter = req.POST.get('select_quarter')
        year = req.POST.get('input_year')
        print('quarter',quarter,type(quarter))
        print('year',year,type(year))
        quarter = int(quarter)
        year = int(year)

        len_quater = get_month_dates(year,quarter)
        print('len_quater',len_quater)
        show_text =f'ไตรมาสที่ {quarter} ปี {year}'
        list_quater = get_list_quarter(quarter)
        print('list_quater',list_quater)
        app = call_quarter(len_quater,list_quater)

        add_to_session(req,app)
  
    else:

        current = datetime.now().date()
        year = current.year
        month = current.month
        print('month_t',month)
        quarter = get_quarter(month)
        print('quarter',quarter)
        len_quarter = get_month_dates(year,quarter)
        print('len_quater',len_quarter)
        show_text =f'ไตรมาสที่ {quarter} ปี {year}'
        list_quarter = get_list_quarter(quarter)
        app = call_quarter(len_quarter,list_quarter)
        print('app',app)
        add_to_session(req,app)

    month_data = 'month'
    quater_data = 'quater'

    income,expenses,income_compare,expenses_compare,success,cancel,success_compare,cancel_compare = get_quarter_data(quarter,year)
    user = req.user
    user_check = call_user(user)
    context = {
        'income':income,
        'expenses':expenses,
        'income_compare':income_compare,
        'expenses_compare':expenses_compare,
        'success':success,
        'cancel':cancel,
        'success_compare':success_compare,
        'cancel_compare':cancel_compare,
        'month_data':month_data,
        'quater_data':quater_data,
        'show_text':show_text,
        'mark':mark,
        'select_quarter':select_quarter,
        'quarter':quarter,
        'year':year,
        'user':user_check
    }
    return render(req,'dashboard/home.html',context)

def get_excel(range_date=None):
    if range_date:
        transactions = Transaction.objects.filter(transaction_type__in=['income', 'expenses'], date__range=range_date).order_by('date')
    else:
        transactions = Transaction.objects.all().order_by('date')

    # Dictionary to store data for each transaction type
    data_by_type = {'income': [], 'expenses': [], 'leftover': []}

    # Iterate over transactions and group them by transaction type
    for transaction in transactions:
        formatted_date = transaction.date.strftime('%Y/%m/%d')
        type_str = None
        if transaction.transaction_type == 'income':
            type_str = 'รายรับ'
        elif transaction.transaction_type == 'expenses':
            type_str = 'รายจ่าย'
        elif transaction.transaction_type == 'leftover':
            type_str = 'คงเหลือ'

        data_by_type[transaction.transaction_type].append({
            'วันที่': formatted_date,
            'ชื่อรายการอาหาร/วัตถุดิบ': transaction.name,
            'จำนวน': transaction.amount,
            'ราคา': transaction.price,
            'ราคารวม': transaction.total_price,
            'ประเภท': type_str
        })

    # Create Excel file with multiple sheets
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        for transaction_type, data in data_by_type.items():
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=transaction_type, index=False)

    # Create HTTP response with Excel file content
    response = HttpResponse(excel_buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Report_Finacial.xlsx"'

    return response
@login_required
def download_excel(req):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    res = get_excel()
    return res

@login_required
def download_range(req):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    if req.method == 'POST':
        start = req.POST.get('start_month')
        end = req.POST.get('end_month')
        print(start,'start')
        print(end,'end')
        start_date = datetime.strptime(start, '%Y-%m')
        end_date = datetime.strptime(end, '%Y-%m')

        start_date = start_date.replace(day=1)
        end_date = (end_date + relativedelta.relativedelta(day=31))
        
        res = get_excel((start_date,end_date))
        return res
        
    else:
       return render(req,'dashboard/download_page.html')
def reason_time(req):
    reason = CancelReason.objects.all()
    time = TimeReceive.objects.all()
    user = req.user
    user_check = call_user(user)

    return render(req,'dashboard/reason_time.html',{
        'reason':reason,
        'time':time,
        'user':user_check
    })

@login_required
def delete_reason(req,id):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    cancel = CancelReason.objects.get(pk=id)
    if cancel:
        cancel.delete()
        return redirect('reason_time')
    
@login_required
def delete_time(req,id):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    time = TimeReceive.objects.get(pk=id)
    if time:
        time.delete()
        return redirect('reason_time')
    
@login_required
def save_reason(req):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    if req.method == "POST":
        reason = req.POST.get('reason')
        use_with = req.POST.get('use_with')
        print(reason,use_with)
        if reason and use_with :
            check = CancelReason.objects.filter(reason=reason)
            print(len(check))
            if check.exists():
                for c in check:
                    if c.use_with == use_with :
                        messages.error(req, f'เหตุผลนี้ถูกสร้างไว้เเล้ว :  {reason}')
                        return redirect('reason_time')
                    if c.use_with != use_with :
                        reason_db = CancelReason.objects.create(reason=reason,use_with=use_with)
            else:
                reason_db = CancelReason.objects.create(reason=reason,use_with=use_with)
            return redirect('reason_time')
        else:
            return redirect('reason_time')

@login_required
def save_time(req):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    if req.method == "POST":
        time = req.POST.get('time')
        print(time)
        if time:
            check = TimeReceive.objects.filter(time_receive=time).first()
            if check :
                messages.error(req, f'มีเวลานัดรับนี้เเล้ว :{time}')
                return redirect('reason_time')
            else:
                reason_db = TimeReceive.objects.create(time_receive=time)
        return redirect('reason_time')
    else:
        return redirect('reason_time')

