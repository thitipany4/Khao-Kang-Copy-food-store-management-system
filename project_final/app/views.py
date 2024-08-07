from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from django.db.models import Case, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from app.forms import *
#from linebot import LineBotApi
#from linebot.models import TextSendMessage
from app.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .getdate import getdate
from .message_admin import *
from .generate_code import generate_random_system_code
from .clear_session import *
from .line_login import LineLogin
from .calculator import calculator
from .forms import FormNote
from .utils import IAECalendar
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from datetime import datetime
#------------------------------------------------------------------
def is_superuser(user):
    return user.is_authenticated and user.is_superuser

        
# Create your views here.
def before_login(req):
    return render(req,'register/before_login.html')

class HomeView(View):
     def get(self, req, *args, **kwargs):
# def home(req):
        #key = check()
        date = getdate()
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        is_weekend = date_obj.weekday() in [5, 6] 
        print(is_weekend)
        food_sale = Historysale.objects.filter(date_field=date)
        foods = Food.objects.all()
        print(food_sale)
        list_food = []
        for food in food_sale:
            if food.options != None and food.options != 'ไม่ได้เลือก':
                print(food)
                list_food.append(food)
        context ={
            'food':list_food,
            'food_list':foods,
            'is_weekend':is_weekend,
        }
        return render(req,'app/home.html',context)

def about_us(req):
    return render(req,'app/aboutus.html')

# @login_required
# def create(req):
#     if not is_superuser(req.user):
#         messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
#         return redirect('profile') 
#     form = FoodForm()
#     if req.method =='POST':
#         form = FoodForm(req.POST,req.FILES)
#         if form.is_valid():
#             name_form = form.instance.name
#             check_name = Food.objects.filter(name=form.instance.name).first()
#             if check_name:
#                 messages.error(req, f"ขออภัยค่ะ ไม่สามารถสร้างเมนู {name_form} ได้ เนื่องจากมีเมนูนี้อยู่ในระบบเเล้ว กรุณาตรวจสอบข้อมูลของท่านอีกครั้งค่ะ")
#                 return redirect('managefood')
#             else:
#                 form.save()
#             return redirect('managefood')
#     context = {
#         'form':form}
#     return render(req,'app/create.html',context)
@method_decorator(login_required, name='dispatch')
class AddFoodView(View):
    def get(self, req, *args, **kwargs):
        if not is_superuser(req.user):
            messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
            return redirect('profile')
        
        form = FoodForm()
        context = {
            'form': form
        }
        return render(req, 'app/create.html', context)
    
    def post(self, req, *args, **kwargs):
        if not is_superuser(req.user):
            messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
            return redirect('profile')
        
        form = FoodForm(req.POST, req.FILES)
        if form.is_valid():
            name_form = form.instance.name
            check_name = Food.objects.filter(name=name_form).first()
            if check_name:
                messages.error(req, f"ขออภัยค่ะ ไม่สามารถสร้างเมนู {name_form} ได้ เนื่องจากมีเมนูนี้อยู่ในระบบเเล้ว กรุณาตรวจสอบข้อมูลของท่านอีกครั้งค่ะ")
                return redirect('managefood')
            else:
                form.save()
                return redirect('managefood')
        
        context = {
            'form': form
        }
        return render(req, 'app/create.html', context)
    
def search(req):
    if req.method =='POST':
        text = req.POST['text-search']
        if text:
            food = Food.objects.filter(name__contains=text)
            if food:
                return render(req,'app/search.html',{'food':food,'text':text})
            else:
                return render(req,'app/search.html',{'text':'ไม่พบเมนูอาหารที่ท่านค้นหา'}) 
        else:
            return render(req,'app/search.html',{'text':'กรุณาเพิ่มเมนูอาหารที่ท่านต้องการค้นหา'}) 

        
    else:
        return render(req,'app/search.html',{'text':'กรุณาเพิ่มเมนูอาหารที่ท่านต้องการค้นหา'}) 

@login_required
def select_date(req):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    if req.method == 'POST':
        form_date = DateForm(req.POST)
        if form_date.is_valid():
            date = form_date.cleaned_data['date_field']
            get_date = getdate(date)
            currect_date = getdate(datetime.now().date())
            food_history = Historysale.objects.filter(date_field=get_date)
            form_date = DateForm()
            thai_date = getdate(None, get_date)
            context = {
                'date': get_date,
                'thai_date': thai_date,
                'food': food_history,
                'form': form_date,
}
            if currect_date != get_date:
                return render(req, 'app/historysales.html', context)
            else:
                return redirect('managefood')
    else:
        return redirect('managefood')

def clearfood(req):
    if req.method=='POST':
        date = getdate()
        foods = Historysale.objects.filter( date_field=date)
        for f in foods:
            if f.options != None:
                f.options = None
                f.save()
        return redirect('managefood')
    else:
        return redirect('managefood')
    
@login_required
def updatefood(req,id):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    if req.method=='GET':
        food = Food.objects.get(pk=id)
        form = FoodForm(instance=food)
    else:
        food = Food.objects.get(pk=id)
        form = FoodForm(req.POST,req.FILES,instance=food)
        old_name = food.name
        if form.is_valid():
            name_form = form.instance.name
            check_name = Food.objects.filter(name=form.instance.name).first()
            if old_name != name_form and check_name:
                messages.error(req, f"ขออภัยค่ะ ไม่สามารถแก้ไข {old_name} เป็น {name_form} ได้ เนื่องจากมีเมนูนี้อยู่ในระบบเเล้ว")
                return redirect('updatefood',id=id)
            else:
                form.save()
                return redirect('managefood')
    context ={
        'food':food,
        'form':form,}
    return render(req,'app/updatefood.html',context)

# @login_required
# def profile(req,username):
#     if req.method=='GET':
#         user =  get_object_or_404(User,username=username)
#         member = Member.objects.get(user=user)
#         form = MemberForm(instance=member)
#     elif req.method=='POST':
#         user =  get_object_or_404(User,username=username)
#         member = Member.objects.get(user=user)
#         form = MemberForm(req.POST,req.FILES,instance=member)
#         if form.is_valid():
#             phone_number = form.cleaned_data['phone_number']
#             gender = form.cleaned_data['gender']
#             print(phone_number)
#             if len(phone_number) != 10 or not phone_number.isdigit():
#                 messages.error(req, 'รูปแบบเบอร์โทรศัพท์ไม่ถูกต้อง')
#                 print(messages.error)
#                 return redirect('profile',username=username)
#             form.instance.age = req.POST.get('age')
#             form.instance.gender = gender
#             form.save()
#             messages.success(req, 'บันทึกข้อมูลสำเร็จ')
#             return redirect('profile',username=username)
#         else:
#             messages.error(req, 'รูปแบบเบอร์โทรศัพท์ไม่ถูกต้องssss')
#             return redirect('profile',username=username)
#     context ={
#         'member':member,
#         'form':form,}
#     return render(req,'app/profile.html',context)
@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, req, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        member = Member.objects.get(user=user)
        form = MemberForm(instance=member)
        context = {
            'member': member,
            'form': form,
        }
        return render(req, 'app/profile.html', context)

    def post(self, req, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        member = Member.objects.get(user=user)
        form = MemberForm(req.POST, req.FILES, instance=member)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            gender = form.cleaned_data['gender']
            if len(phone_number) != 10 or not phone_number.isdigit():
                messages.error(req, 'รูปแบบเบอร์โทรศัพท์ไม่ถูกต้อง')
                return redirect('profile', username=username)
            form.instance.age = req.POST.get('age')
            form.instance.gender = gender
            form.save()
            messages.success(req, 'บันทึกข้อมูลสำเร็จ')
            return redirect('profile', username=username)
        else:
            messages.error(req, 'รูปแบบเบอร์โทรศัพท์ไม่ถูกต้องssss')
            return redirect('profile', username=username)

        # context = {
        #     'member': member,
        #     'form': form,
        # }
        # return render(req, 'app/profile.html', context)
    
@login_required           
def delete(req,id):
    #return render(request, 'kawai/delete.html')
    f = Food.objects.get(pk=id)
    f.delete()
    return redirect('managefood')

def foodview(req, id=None, target=None):
    if id:
        orderby = 'not order'
        food = Food.objects.get(pk=id)
        review = Reviewfood.objects.filter(food=food)
        # memver = Member.objects.all()
        orderby =review.order_by('-created')
        star_range = [1,2,3,4,5]
        star_count = defaultdict(int)

        for rating in review:
            star_count[rating.rating] += 1
        if review.exists():
            count_score = len(review)
            average_score = sum(rating.rating for rating in review) / count_score
            average_score = round(average_score,2)
        else:
            context = {
            'food': food,
            'review': orderby,
        }
            return render(req, 'app/foodview.html', context) 
        ratings = []
        for i in range(1, 6):
            rating_count = star_count[i]
            width = (rating_count / count_score) * 100 if count_score > 0 else 0
            ratings.append({'rating': i, 'count': rating_count, 'width': width})
        if req.method == "GET" and target:
            if target == 'lastest':
                orderby = review.order_by('-created')
            else:
                orderby = review.order_by('-rating')
        
        context = {
            'food': food,
            'review': orderby,
            'star_range': star_range,
            'count_score':count_score,
            'ratings':ratings,
            'average_score':average_score,
        }
        return render(req, 'app/foodview.html', context)
    return render(req, 'app/foodview.html', {})

#@login_required
# def reviewfood(req,id):
#     food = Food.objects.get(pk=id)
#     if req.method =='GET':
#         form = ReviewFood(instance=food)
#     else:
#         form = ReviewFood(req.POST,req.FILES)
#         form.instance.food = food
#         if form.is_valid():
#             review = form.save(commit=False)
#             member = Member.objects.get(user=req.user)
#             print(form.instance.rating)
#             review.owner = member
#             food.quantity_review +=1
#             if food.quantity_review !=0:
#                 #คะแนนเดิม + คะแนนใหม่ หารด้วยจำนวนรีวิวทั้งหมด 
#                 average_score = (food.score * (int(food.quantity_review) - 1) + form.instance.rating) / food.quantity_review
#                 food.score = round(average_score, 2)
#             food.save()
#             review.save()
#             return redirect('foodview',id=id)
#         else:
#             messages.error(req, 'กรุณาป้อนคะแนนรีวิวที่ท่านต้องการ')
#             return redirect('review',id=id)
#     context = {
#         'form':form,
#         'food':food,
#     }
#     return render(req,'app/review.html',context)
@method_decorator(login_required, name='dispatch')
class ReviewFoodView(View):
    def get(self, req, id, *args, **kwargs):
        food = get_object_or_404(Food, pk=id)
        form = ReviewFood(instance=food)
        context = {'form': form,'food': food,}
        return render(req, 'app/review.html', context)
    def post(self, req, id, *args, **kwargs):
        food = get_object_or_404(Food, pk=id)
        form = ReviewFood(req.POST, req.FILES)
        form.instance.food = food
        if form.is_valid():
            review = form.save(commit=False)
            member = Member.objects.get(user=req.user)
            review.owner = member
            food.quantity_review += 1
            if food.quantity_review != 0:
                # Calculate the new average score
                average_score = (food.score * (food.quantity_review - 1) + form.instance.rating) / food.quantity_review
                food.score = round(average_score, 2)
            food.save()
            review.save()
            return redirect('foodview', id=id)
        else:
            messages.error(req, 'กรุณาป้อนคะแนนรีวิวที่ท่านต้องการ')
            return redirect('review', id=id)
# @login_required
# def managefood(req, date=None):
#     if not is_superuser(req.user):
#         messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
#         return redirect('home') 
#     if req.method == 'POST':
#         quantity = req.POST.getlist('input_quantity')
#         food_ids = req.POST.getlist('food_id')
#         options = req.POST.getlist('options')
#         if len(food_ids) == len(options):
#             for id, option,quantity in zip(food_ids, options,quantity):
#                 food_item = Food.objects.get(pk=id)
#                 if option == 'ไม่ได้เลือก':
#                     found = Historysale.objects.filter(food_id=food_item.id, date_field=date).first()
#                     if found:
#                         found.options = option
#                         found.delete()
#                 elif option in ['วางขาย', 'ขายหมดแล้ว']:
#                     found = Historysale.objects.filter(food_id=food_item.id, date_field=date).first()
#                     if not found and quantity == '':
#                         food = Food.objects.get(pk=id)
#                         messages.error(req,f'เมนู {food} ไม่ได้เพิ่มจำนวนที่ต้องการขาย')
#                         return redirect('managefood')
#                     if found:
#                         if found.options != option:
#                             if option == 'ขายหมดแล้ว':
#                                 found.options = option
#                                 found.save()
#                             else:
#                                 found.quantity = quantity
#                                 found.options = option
#                                 found.save()
#                         else:
#                             if quantity:
#                                 if option == 'ขายหมดแล้ว':
#                                     pass
#                                 else:
#                                     found.quantity = quantity
#                                     found.save()
#                     else:
#                         history_sale = Historysale.objects.create(food=food_item, date_field=date,quantity=quantity,options='วางขาย')
#         return redirect('managefood')
#     else:
#         food = Food.objects.all()
#         form_date = DateForm()
#         get_date = getdate()
#         thai_date = getdate(None,get_date)
#         history = Historysale.objects.filter(date_field=get_date)
#         list_options = []
#         options = Historysale.OPTIONS
#         for o in options:
#             list_options.append(o[0])
#         list_food =[]
#         for food in food:
#             found_item = ''
#             for item in history:
#                 if food == item.food:
#                     found_item = item
#                     break
#             if found_item:
#                 list_food.append((food,found_item))
#             else:
#                 list_food.append((food,''))
#         context ={
#             'date':get_date,
#             'thai_date':thai_date,
#             'food':food,
#             'form':form_date,
#             'list_food':list_food,
#             'options':list_options,}
#         return render(req,'app/managefood.html',context)

@method_decorator(login_required, name='dispatch')
class ManageFoodView(View):
    def get(self, req, date=None):
        if not is_superuser(req.user):
            messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
            return redirect('home')

        form_date = DateForm()
        get_date = getdate()
        thai_date = getdate(None, get_date)
        history = Historysale.objects.filter(date_field=get_date)
        list_options = [o[0] for o in Historysale.OPTIONS]
        list_food = []

        for food in Food.objects.all():
            found_item = history.filter(food=food).first()
            list_food.append((food, found_item if found_item else ''))

        context = {
            'date': get_date,
            'thai_date': thai_date,
            'form': form_date,
            'list_food': list_food,
            'options': list_options,
        }
        return render(req, 'app/managefood.html', context)

    def post(self, req, date=None):
        if not is_superuser(req.user):
            messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
            return redirect('home')

        quantity = req.POST.getlist('input_quantity')
        food_ids = req.POST.getlist('food_id')
        options = req.POST.getlist('options')

        if len(food_ids) == len(options):
            for id, option, quantity in zip(food_ids, options, quantity):
                food_item = Food.objects.get(pk=id)

                if option == 'ไม่ได้เลือก':
                    found = Historysale.objects.filter(food_id=food_item.id, date_field=date).first()
                    if found:
                        found.options = option
                        found.delete()

                elif option in ['วางขาย', 'ขายหมดแล้ว']:
                    found = Historysale.objects.filter(food_id=food_item.id, date_field=date).first()

                    if not found and quantity == '':
                        messages.error(req, f'เมนู {food_item} ไม่ได้เพิ่มจำนวนที่ต้องการขาย')
                        return redirect('managefood')

                    if found:
                        if found.options != option:
                            if option == 'ขายหมดแล้ว':
                                found.options = option
                                found.save()
                            else:
                                found.quantity = quantity
                                found.options = option
                                found.save()
                        else:
                            if quantity and option != 'ขายหมดแล้ว':
                                found.quantity = quantity
                                found.save()

                    else:
                        Historysale.objects.create(food=food_item, date_field=date, quantity=quantity, options='วางขาย')

        return redirect('managefood')


def line_login(request):
    line = LineLogin()
    auth_link = line.get_link()  

    return redirect(auth_link)
 
def line_callback(request):
    if 'code' in request.GET and 'state' in request.GET:
        code = request.GET['code']
        state = request.GET['state']
        line = LineLogin()
        token = line.token(code, state)
        if token.get('error'):
            return redirect('home')
        if token.get('id_token'):
            profile = line.profile_from_id_token(token)
            request.session['profile'] = profile
            print('user id',profile.get('user_id'))
            user_id = profile.get('name')  
            user = User.objects.filter(username=user_id).first()
            print(user)
            print('user_id',user_id)
            if user:
                    auth_login(request, user)
                    return redirect('home') 
            else:
                print('you in else')
                 #เป็นการตรวจสอบสถานะการล็อกอินของผู้ใช้ เพื่อให้รหัสของคุณทำงานอย่างถูกต้องโดยขึ้นอยู่กับว่าผู้ใช้มีการล็อกอินอยู่หรือไม่ และจัดการกับกรณีที่จำเป็นต้องสร้างผู้ใช้ใหม่เท่านั้น
                line_user = request.user if request.user.is_authenticated else User.objects.create_user(username=user_id)
                line_user_profile, created = Member.objects.get_or_create( 
                    #id =profile['user_id'],
                    user=line_user,
                    email=profile['email'],
                    line_id = profile['user_id'],
                    picture=profile['picture'],)
                print('register success')
                auth_login(request, line_user_profile.user)
                print('user:',line_user_profile.user)
                check='check'
                return redirect('qr_code',check=check) 


    return redirect('home')  

def logout(req):
    auth_logout(req)
    return redirect('home')

def get_prev_month(d):
    year = d.year - 1 if d.month == 1 else d.year
    month = d.month - 1 if d.month > 1 else 12
    prev_month_date = d.replace(year=year, month=month)
    return prev_month_date

def get_next_month(d):
    year = d.year + (d.month // 12)
    month = d.month % 12 + 1
    next_month_date = d.replace(year=year, month=month)
    return next_month_date

# @login_required
# def calendar(req,date=None,mark=None):
#     if not is_superuser(req.user):
#         messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
#         return redirect('home') 
#     my_calendar = IAECalendar()
#     if req.method == 'GET':
#         if date and mark =='next_month':
#             d = datetime.strptime(date, '%Y-%m-%d').date()
#             date_str = get_next_month(d)
#             date=getdate(date_str)
#         elif date and mark =='prev_month':
#             d = datetime.strptime(date, '%Y-%m-%d').date()
#             date_str = get_prev_month(d)
#             date=getdate(date_str)
#         else:
#             date = getdate()
#             date_str = datetime.strptime(date, '%Y-%m-%d').date()
#         year = date_str.year
#         month = date_str.month
#         calendar_html = my_calendar.formatmonth(year, month)
#     else:
#         date = req.POST.get('move_to_month') + '-01'
#         if date:
#             d = datetime.strptime(date, '%Y-%m-%d').date()
#             year = d.year
#             month = d.month
#             calendar_html = my_calendar.formatmonth(year, month)
#             note = Transaction.objects.filter(date__year=year, date__month=month)
#             sum_expenses,sum_income= calculator(note)
#             total = sum_income- sum_expenses 
#             context = {'calendar_html': calendar_html,
#                         'date':date,
#                         'total':total,
#                         'sum_expenses':sum_expenses,
#                         'sum_income':sum_income,}
#             return render(req, 'app/calendar_template.html',context)
#         else:
#             return redirect('home')
#     note = Transaction.objects.filter(date__year=date_str.year, date__month=date_str.month)
#     sum_expenses,sum_income= calculator(note)
#     total = sum_income- sum_expenses 
#     context = {'calendar_html': calendar_html,
#                 'date':date,
#                 'total':total,
#                 'sum_expenses':sum_expenses,
#                 'sum_income':sum_income,}
#     return render(req, 'app/calendar_template.html',context)
@method_decorator(login_required, name='dispatch')
class CalendarView(View):
    def get(self, req, date=None, mark=None):
        if not is_superuser(req.user):
            messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
            return redirect('home')
        my_calendar = IAECalendar()
        if date and mark == 'next_month':
            d = datetime.strptime(date, '%Y-%m-%d').date()
            date_str = get_next_month(d)
            date = getdate(date_str)
        elif date and mark == 'prev_month':
            d = datetime.strptime(date, '%Y-%m-%d').date()
            date_str = get_prev_month(d)
            date = getdate(date_str)
        else:
            date = getdate()
            date_str = datetime.strptime(date, '%Y-%m-%d').date()
        year = date_str.year
        month = date_str.month
        calendar_html = my_calendar.formatmonth(year, month)
        note = Transaction.objects.filter(date__year=year, date__month=month)
        sum_expenses, sum_income = calculator(note)
        total = sum_income - sum_expenses
        context = {'calendar_html': calendar_html,'date': date,
        'total': total,'sum_expenses': sum_expenses,'sum_income': sum_income,}
        return render(req, 'app/calendar_template.html', context)

    def post(self, req):
        if not is_superuser(req.user):
            messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
            return redirect('home')
        date = req.POST.get('move_to_month') + '-01'
        if date:
            d = datetime.strptime(date, '%Y-%m-%d').date()
            year = d.year
            month = d.month
            my_calendar = IAECalendar()
            calendar_html = my_calendar.formatmonth(year, month)

            note = Transaction.objects.filter(date__year=year, date__month=month)
            sum_expenses, sum_income = calculator(note)
            total = sum_income - sum_expenses
            context = {'calendar_html': calendar_html,'date': date,
                'total': total,'sum_expenses': sum_expenses,'sum_income': sum_income,}
            return render(req, 'app/calendar_template.html', context)
        else:
            return redirect('home')
# @login_required
# def note(req, date=None,type=None,filter=None):
#     if not is_superuser(req.user):
#         messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
#         return redirect('home') 
#     if req.method == 'POST':
#         name = req.POST.get('name')
#         price = req.POST.get('price')
#         amount = req.POST.get('amount')
#         transaction = req.POST.get('transaction_type')
#         add_data = Transaction.objects.create(
#             name=name,
#             price=price,
#             amount=amount,
#             transaction_type=transaction,
#             date=date,
#             total_price=(int(price)*int(amount))
#         )
#     if filter:
#         if filter == 'most_quatity':
#             note = Transaction.objects.filter(date=date,transaction_type=type).order_by('-amount')
#         elif filter == 'most_price':
#             note = Transaction.objects.filter(date=date,transaction_type=type).order_by('-total_price')
#         elif filter == 'latest':
#             note = Transaction.objects.filter(date=date,transaction_type=type).order_by('-date')
#     else:
#         note = Transaction.objects.filter(date=date,transaction_type=type)
#     sum_expenses,sum_income= calculator(note)
#     most_quatity = 'most_quatity'
#     most_price = 'most_price'
#     latest = 'latest'
#     context = {
#         'note':note,
#         'date':date,
#         'type':type,
#         'sum_expenses':sum_expenses,
#         'sum_income':sum_income,
#         'most_quatity':most_quatity,
#         'most_price':most_price,
#         'latest':latest
#     }
#     return render(req, 'app/note.html',context)
@method_decorator(login_required, name='dispatch')
class AddTransactionView(View):
    def get(self, req, date=None, type=None, filter=None, *args, **kwargs):
        if not is_superuser(req.user):
            messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
            return redirect('home')
        note =''
        if filter:
            if filter == 'most_quatity':
                note = Transaction.objects.filter(date=date, transaction_type=type).order_by('-amount')
            elif filter == 'most_price':
                note = Transaction.objects.filter(date=date, transaction_type=type).order_by('-total_price')
            elif filter == 'latest':
                note = Transaction.objects.filter(date=date, transaction_type=type).order_by('-date')
        else:
            note = Transaction.objects.filter(date=date, transaction_type=type)

        sum_expenses, sum_income = calculator(note)

        context = {
            'note': note,'date': date,'type': type,
            'sum_expenses': sum_expenses,'sum_income': sum_income,
            'most_quatity': 'most_quatity','most_price': 'most_price',
            'latest': 'latest',}
        return render(req, 'app/note.html', context)

    def post(self, req, date=None, type=None, filter=None, *args, **kwargs):
        if not is_superuser(req.user):
            messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
            return redirect('home')
        name = req.POST.get('name')
        price = req.POST.get('price')
        amount = req.POST.get('amount')
        transaction = req.POST.get('transaction_type')
        add_data = Transaction.objects.create(
            name=name, price=price,amount=amount,
            transaction_type=transaction, date=date,
            total_price=(int(price) * int(amount)))
        note =''
        if filter:
            if filter == 'most_quatity':
                note = Transaction.objects.filter(date=date, transaction_type=type).order_by('-amount')
            elif filter == 'most_price':
                note = Transaction.objects.filter(date=date, transaction_type=type).order_by('-total_price')
            elif filter == 'latest':
                note = Transaction.objects.filter(date=date, transaction_type=type).order_by('-date')
        else:
            note = Transaction.objects.filter(date=date, transaction_type=type)

        sum_expenses, sum_income = calculator(note)

        context = {
            'note': note,'date': date,'type': type,
            'sum_expenses': sum_expenses,'sum_income': sum_income,
            'most_quatity': 'most_quatity','most_price': 'most_price',
            'latest': 'latest',}
        return render(req, 'app/note.html', context)

@login_required
def delete_note(req,date,type,id):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    note = Transaction.objects.get(pk=id)
    if note:
        note.delete()
        return redirect('note', date=date, type=type)
    else:
        return redirect('note', date=date, type=type)

@login_required
def show_note(req,date=None,type=None):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    if type:
        if type == 'expenses':
            note = Transaction.objects.filter(date=date).annotate(
            expense_order=Case(When(transaction_type='expenses', then=Value(0)),default=Value(1))).order_by('expense_order')
        elif type == 'income':
            note = Transaction.objects.filter(date=date).annotate(
            income_order=Case(When(transaction_type='income', then=Value(0)),default=Value(1))).order_by('income_order')
        elif type == 'leftover':
            note = Transaction.objects.filter(date=date).annotate(
            leftover_order=Case(When(transaction_type='leftover', then=Value(0)),default=Value(1))).order_by('leftover_order')
    else:
        note = Transaction.objects.filter(date=date)    
    sum_expenses,sum_income= calculator(note)
    total = sum_income- sum_expenses 
    expenses= 'expenses'
    income ='income'
    leftover ='leftover'
    context = {
         'sum_expenses':sum_expenses,
         'sum_income':sum_income,
         'total':total,
         'date':date,
         'note':note,
         'expenses':expenses,
         'income':income,
         'leftover':leftover,
    }
    return render(req, 'app/show-note.html',context )

@login_required
def create_cart(request):
    user = request.user
    member = Member.objects.filter(user=user).first()
    if not member.first_name or not member.last_name or not member.phone_number:
        messages.error(request,'ข้อความกรุณากรอบข้อมูลส่วนตัวให้ครบถ้วน')
        return redirect('profile',username=user)
    order = Order.objects.filter(user=request.user,checkout=False).first()
    print(order)
    if order :
        print('in order condition ')
        if (timezone.now() - order.created_at).total_seconds() > 1800:
            order.delete()
            return redirect('create_cart')
        else:
            request.session['order'] = order.ref_code  
            return redirect('view_cart')

    else:
        random_code = generate_random_system_code()
        order = Order.objects.create(total_price=0, ref_code=random_code,user=request.user)
        request.session['order'] = order.ref_code  
        print(order, 'create cart done')
    return redirect('view_cart')

@login_required
def view_cart(request):
    order_id = request.session.get('order')
    total_price = 0
    context={}
    print(order_id)
    if order_id:
        order = get_object_or_404(Order, ref_code=order_id)
        print(order.id)
        order_item1 = OrderItemtype1.objects.filter(order=order)
        order_item2 = OrderItemtype2.objects.filter(order=order)
        for item1 in order_item1:
            total_price += item1.total_price
        for item2 in order_item2:
            total_price += item2.total_price
        type_1 = 'type1'
        type_2 = 'type2'
        context ={
            'order':order,
            'order_item1':order_item1,
            'order_item2':order_item2,
            'type_1':type_1,
            'type_2':type_2,
            'total_price':total_price,
        }
    return render(request, 'app/view_cart.html', context)

@login_required
def delete_cart(request,code):
    if code:
        Order.objects.filter(ref_code=code).delete()
    return redirect('home')

@login_required
def shopping_food_type1(request):
    item = []
    date = getdate()
    food_sale = Historysale.objects.filter(date_field=date)
    for f in food_sale:
        if f.options == 'วางขาย':
            item.append(f)
    return render(request, 'app/shop_food1.html', {'food': item,
                                                         })

@login_required
def modify_cart1(request,ref_code):
    date = getdate()
    foods = Historysale.objects.filter(date_field=date,options='วางขาย')
    items = OrderItemtype1.objects.filter(order__ref_code=ref_code)
    food_item = []
    for food in foods:
        found_item = ''
        for item in items:
            if food.food == item.food:
                found_item = item
                break
        if found_item:
            food_item.append((food,found_item,food.quantity))
        else:
            food_item.append((food,0,food.quantity))
    modify = 'True'
    return render(request, 'app/shop_food1.html', {'food_item': food_item, 'modify':modify})

@login_required
def shopping_food_type2(request):
    item = []
    date = getdate()
    food_sale = Historysale.objects.filter(date_field=date)
    for f in food_sale:
        if f.options == 'วางขาย':
            item.append(f)
    return render(request, 'app/shop_food2.html', {'food': item,
                                                         })
@login_required
def modify_cart2(request,id):
    special = 'False'
    date = getdate()
    food_sale = Historysale.objects.filter(date_field=date,options='วางขาย')
    item = OrderItemtype2.objects.get(pk=id)
    if item.price == 50:
        special = 'True'
    modify = f'{item.id}'
    selected = []
    for i in item.foods.all():
        selected.append(i.id)
    return render(request, 'app/shop_food2.html', {'food': food_sale, 'selected':selected,'modify':modify,'special':special,'item':item,})

@login_required
def add_to_cart(request,type,modify=None):
    if request.method == 'POST':
        if type=='type1':
            product_ids = request.POST.getlist('product_id')
            quantities = request.POST.getlist('quantity')
            order_id = request.session.get('order')
            for product_id, quantity in zip(product_ids, quantities):
                product = get_object_or_404(Food, pk=product_id)
                quantity = int(quantity)  
                if quantity == 0:  
                    order = get_object_or_404(Order, ref_code=order_id)
                    product = OrderItemtype1.objects.filter(food=product,order=order).first()
                    if product:
                        product.delete()
                        continue
                    else:
                        continue
                if not order_id:
                    random_code = generate_random_system_code()
                    order = Order.objects.create(total_price=0, ref_code=random_code, user=request.user)
                    request.session['order'] = random_code
                else:
                    order = Order.objects.get(ref_code=order_id)

                order_item = OrderItemtype1.objects.filter(order=order, food=product).first()
                if order_item:
                    pass
                else:
                    order_item = OrderItemtype1.objects.create(order=order, food=product)
                if not modify :
                    order_item.quantity += quantity
                    order_item.total_price += (product.price * quantity)
                else:
                    if order_item.quantity != quantity:
                        order_item.total_price += (product.price * quantity)
                        order_item.total_price -= (product.price * order_item.quantity)
                        order_item.quantity = quantity
                    else:
                        pass
                order_item.save()
            return redirect('view_cart')
        else:
            product_ids = request.POST.getlist('product_id')
            quantities = request.POST.get('quantity')
            checked_add = request.POST.getlist('add_to_cart')
            special = request.POST.get('special')
            order_id = request.session.get('order')
            selected_product_ids = [product_id for product_id, checked in zip(product_ids, checked_add) if checked == 'checked']
            selected_products = Food.objects.filter(id__in=selected_product_ids)
            total_quantity = int(quantities)##
            print(total_quantity,'total_quantity')
            if selected_products:
                    food_names = ' + '.join(product.name for product in selected_products)
                    print(food_names,'food_names')
                    if not order_id:
                        random_code = generate_random_system_code()
                        order = Order.objects.create(total_price=0, ref_code=random_code,user=request.user)
                        request.session['order'] = order.ref_code
                    else:
                        order = get_object_or_404(Order, ref_code=order_id)
                    if modify:
                        id =int(modify)
                        order_item = OrderItemtype2.objects.get(pk=id)
                        order_item.name = food_names
                    else:
                        check_item = OrderItemtype2.objects.filter(order=order,name=food_names).first()
                        if check_item:
                            order_item=check_item
                        else:
                            order_item = OrderItemtype2.objects.create(order=order, quantity=0
                                                                       ,name=food_names)
                    if total_quantity == 0 :
                        order_item.delete()
                        return redirect('view_cart')
                    order_item.foods.set(selected_products)
                    if not modify :
                        if special == 'not checked':
                            order_item.price = 40
                        else:
                            order_item.price = 50
                        order_item.quantity += total_quantity
                        order_item.total_price += (order_item.price * total_quantity)
                    else:
                        original_price = None
                        if special == 'not checked':
                            if order_item.price == 50:
                                order_item.price = 40
                                original_price = 50
                            else:
                                order_item.price = 40
                        else:
                            if order_item.price == 40:
                                order_item.price = 50
                                original_price = 40
                            else:
                                order_item.price = 50
                        if order_item.quantity != total_quantity:
                            if original_price:
                                order_item.total_price -= (original_price*order_item.quantity)
                                order_item.total_price += (order_item.price*total_quantity)
                            else:
                                order_item.total_price -= (order_item.price*order_item.quantity)
                                order_item.total_price += (order_item.price*total_quantity)
                            order_item.quantity = total_quantity
                        else:
                            if original_price:
                                order_item.total_price -= (original_price*order_item.quantity)
                                order_item.total_price += (order_item.price*order_item.quantity)         
                    order_item.save()
                    return redirect('view_cart')
# @method_decorator(login_required, name='dispatch')
# class AddToCartView(View):
#     def post(self, request, type, modify=None):
#         if type == 'type1':
#             return self.add_type1(request, modify)
#         else:
#             return self.add_type2(request, modify)
    
#     def add_type1(self, request, modify):
#         product_ids = request.POST.getlist('product_id')
#         quantities = request.POST.getlist('quantity')
#         order_id = request.session.get('order')
        
#         for product_id, quantity in zip(product_ids, quantities):
#             product = get_object_or_404(Food, pk=product_id)
#             quantity = int(quantity)
            
#             if quantity == 0:
#                 order = get_object_or_404(Order, ref_code=order_id)
#                 order_item = OrderItemtype1.objects.filter(food=product, order=order).first()
#                 if order_item:
#                     order_item.delete()
#                 continue

#             if not order_id:
#                 random_code = generate_random_system_code()
#                 order = Order.objects.create(total_price=0, ref_code=random_code, user=request.user)
#                 request.session['order'] = random_code
#             else:
#                 order = Order.objects.get(ref_code=order_id)

#             order_item = OrderItemtype1.objects.filter(order=order, food=product).first()
#             if not order_item:
#                 order_item = OrderItemtype1.objects.create(order=order, food=product)
            
#             if not modify:
#                 order_item.quantity += quantity
#                 order_item.total_price += (product.price * quantity)
#             else:
#                 if order_item.quantity != quantity:
#                     order_item.total_price += (product.price * quantity)
#                     order_item.total_price -= (product.price * order_item.quantity)
#                     order_item.quantity = quantity

#             order_item.save()
        
#         return redirect('view_cart')
    
#     def add_type2(self, request, modify):
#         product_ids = request.POST.getlist('product_id')
#         quantities = request.POST.get('quantity')
#         checked_add = request.POST.getlist('add_to_cart')
#         special = request.POST.get('special')
#         order_id = request.session.get('order')
        
#         selected_product_ids = [product_id for product_id, checked in zip(product_ids, checked_add) if checked == 'checked']
#         selected_products = Food.objects.filter(id__in=selected_product_ids)
#         total_quantity = int(quantities)
        
#         if selected_products:
#             food_names = ' + '.join(product.name for product in selected_products)
            
#             if not order_id:
#                 random_code = generate_random_system_code()
#                 order = Order.objects.create(total_price=0, ref_code=random_code, user=request.user)
#                 request.session['order'] = order.ref_code
#             else:
#                 order = get_object_or_404(Order, ref_code=order_id)
            
#             if modify:
#                 order_item = get_object_or_404(OrderItemtype2, pk=int(modify))
#                 order_item.name = food_names
#             else:
#                 order_item = OrderItemtype2.objects.filter(order=order, name=food_names).first()
#                 if not order_item:
#                     order_item = OrderItemtype2.objects.create(order=order, quantity=0, name=food_names)
            
#             if total_quantity == 0:
#                 order_item.delete()
#                 return redirect('view_cart')

#             order_item.foods.set(selected_products)

#             if not modify:
#                 order_item.price = 40 if special == 'not checked' else 50
#                 order_item.quantity += total_quantity
#                 order_item.total_price += (order_item.price * total_quantity)
#             else:
#                 original_price = None
#                 if special == 'not checked':
#                     if order_item.price == 50:
#                         original_price = 50
#                     order_item.price = 40
#                 else:
#                     if order_item.price == 40:
#                         original_price = 40
#                     order_item.price = 50

#                 if order_item.quantity != total_quantity:
#                     if original_price:
#                         order_item.total_price -= (original_price * order_item.quantity)
#                     order_item.total_price += (order_item.price * total_quantity)
#                     order_item.quantity = total_quantity
#                 elif original_price:
#                     order_item.total_price -= (original_price * order_item.quantity)
#                     order_item.total_price += (order_item.price * order_item.quantity)
            
#             order_item.save()
#             return redirect('view_cart')
@login_required           
def delete_from_cart(request, product_id,type):
    if type == 'type1':
        product = get_object_or_404(OrderItemtype1, pk=product_id) 
        product.delete()
    else:
        product = get_object_or_404(OrderItemtype2, id=product_id) 
        product.delete()
    return redirect('view_cart')
 
@method_decorator(login_required, name='dispatch')         
class CheckoutView(View):
    def get(self, request, ref_code, total_price):
        order = get_object_or_404(Order, ref_code=ref_code)
        total_price = int(total_price)
        order_item1 = OrderItemtype1.objects.filter(order=order)
        order_item2 = OrderItemtype2.objects.filter(order=order)
        if not order_item1 and not order_item2:
            messages.error(request, 'ตะกร้าของท่านไม่มีเมนูอาหาร')
            return redirect('view_cart')
        db_time = TimeReceive.objects.all()
        selected_times = []
        bangkok_tz = pytz.timezone('Asia/Bangkok')
        current_time_bangkok = datetime.now(bangkok_tz)
        for time_slot in db_time:
            slot_time = datetime.strptime(time_slot.time_receive.split()[0], "%H:%M")
            slot_datetime = bangkok_tz.localize(datetime.combine(current_time_bangkok.date(), slot_time.time()))
            if slot_datetime > current_time_bangkok:
                selected_times.append(time_slot)
        selected_times.sort(key=lambda x: x.time_receive.split()[0])
        context = {'order': order,'total_price': total_price,
            'select_time': selected_times,'order_item1': order_item1,'order_item2': order_item2,}
        return render(request, 'app/checkout.html', context)

def get_quatity(obj):
    date = getdate()
    food_sale = get_object_or_404(Historysale,food=obj,date_field=date)
    if food_sale:
        return food_sale
    else:
        return redirect('home')
           
def create_transaction(obj1,obj2):
    date = getdate()
    if obj1:
        for i in obj1:
            transaction = Transaction.objects.create(
                    name=i.food.name + ' (จากระบบ)',
                    price=i.food.price,
                    amount=i.quantity,
                    transaction_type='income',
                    date=date,
                    total_price=i.total_price

            )
            print('transaction',transaction)
    if obj2:
        for i in obj2:
            transaction = Transaction.objects.create(
                    name=i.name + ' (จากระบบ)',
                    price=i.price,
                    amount=i.quantity,
                    transaction_type='income',
                    date=date,
                    total_price=i.total_price

            )
            print('transaction',transaction)

# @login_required           
# def user_confirm_order(request, ref_code=None):
#     if ref_code is None:
#         order_id = request.session.pop('order', None)
#         return redirect('home')
#     if request.method == 'POST':
#         time = request.POST.get('select_time')
#         order = get_object_or_404(Order, ref_code=ref_code)
#         order_item1 = OrderItemtype1.objects.filter(order=order)
#         order_item2 = OrderItemtype2.objects.filter(order=order)
#         if order_item1:
#             for i in order_item1:
#                 food = Food.objects.filter(pk=i.food.id).first()
#                 food_sale = get_quatity(food)
#                 if food_sale.quantity - i.quantity < 0 :
#                     messages.error(request,f'จำนวน {food_sale.food.name} ไม่เพียงพอ')
#                     return redirect('view_cart')
#                 elif food_sale.quantity - i.quantity == 0 :
#                     food_sale.quantity -= i.quantity 
#                     food_sale.options = 'ขายหมดแล้ว'
#                 else:
#                     food_sale.quantity -= i.quantity 
#                 order.total_price += i.total_price
#                 order.save()
#                 food_sale.save()
#         if order_item2:
#             for item in order_item2:
#                 for i in item.foods.all():
#                     foods = get_object_or_404(Food,pk=i.id)
#                     food_sale2 = get_quatity(foods)
#                     if food_sale2.quantity - item.quantity < 0 :
#                         messages.error(request,f'จำนวน {food_sale2.food.name} ไม่เพียงพอ')
#                         return redirect('view_cart')
#                     elif food_sale2.quantity - item.quantity == 0 :
#                         food_sale2.quantity -= item.quantity 
#                         food_sale2.options = 'ขายหมดแล้ว'
#                         food_sale2.save()
#                     else:
#                         food_sale2.quantity -= item.quantity 
#                         food_sale2.save()
#                 if item.total_price != 0:
#                     order.total_price += item.total_price
#                     order.save()
#         request.session.pop('order', None)
#         date= getdate()
#         order.checkout = True
#         order.time_receive=time
#         order.save()
#         message_to_admin(order)

#         context ={  
#             'order':order,
#             'order_item1':order_item1,
#             'order_item2':order_item2,}
#         return render(request, 'app/order_confirmation.html', context)

    
@method_decorator(login_required, name='dispatch')
class UserConfirmOrderView(View):
    def post(self, request, ref_code=None):
        if ref_code is None:
            order_id = request.session.pop('order', None)
            return redirect('home')
        time = request.POST.get('select_time')
        order = get_object_or_404(Order, ref_code=ref_code)
        order_item1 = OrderItemtype1.objects.filter(order=order)
        order_item2 = OrderItemtype2.objects.filter(order=order)
        if order_item1:
            for i in order_item1:
                food = Food.objects.filter(pk=i.food.id).first()
                food_sale = get_quatity(food)
                if food_sale.quantity - i.quantity < 0 :
                    messages.error(request,f'จำนวน {food_sale.food.name} ไม่เพียงพอ')
                    return redirect('view_cart')
                elif food_sale.quantity - i.quantity == 0 :
                    food_sale.quantity -= i.quantity 
                    food_sale.options = 'ขายหมดแล้ว'
                else:
                    food_sale.quantity -= i.quantity 
                order.total_price += i.total_price
                order.save()
                food_sale.save()
        if order_item2:
            for item in order_item2:
                for i in item.foods.all():
                    foods = get_object_or_404(Food,pk=i.id)
                    food_sale2 = get_quatity(foods)
                    if food_sale2.quantity - item.quantity < 0 :
                        messages.error(request,f'จำนวน {food_sale2.food.name} ไม่เพียงพอ')
                        return redirect('view_cart')
                    elif food_sale2.quantity - item.quantity == 0 :
                        food_sale2.quantity -= item.quantity 
                        food_sale2.options = 'ขายหมดแล้ว'
                        food_sale2.save()
                    else:
                        food_sale2.quantity -= item.quantity 
                        food_sale2.save()
                if item.total_price != 0:
                    order.total_price += item.total_price
                    order.save()
        request.session.pop('order', None)
        date= getdate()
        order.checkout = True
        order.time_receive=time
        order.save()
        message_to_admin(order)
        context ={  
            'order':order,
            'order_item1':order_item1,
            'order_item2':order_item2,}
        return render(request, 'app/order_confirmation.html', context)
    
# @login_required           
# def admin_confirm_order(request,code=None,status=None,filter=None):
#     if not is_superuser(request.user):
#         messages.error(request, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
#         return redirect('home') 
#     # order = Order.objects.get(pk=order_id)
#     member_list=''
#     if request.method == 'GET':
#         current_date = getdate()
#         thai_date = getdate(None,current_date)
#         print(thai_date)
#         current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
#         print(current_date,'f')
#         orders = Order.objects.filter(created_at__contains=current_date,checkout=True)
#         if filter:
#             orders = filter_history_confirm(orders,filter)
#         else:
#             orders = orders
#         reason =None
#         time =None
#         if orders:
#             reason = CancelReason.objects.filter(use_with='admin')

#             print(reason)
#             time = TimeReceive.objects.all()

#         receive_text ='receive'
#         wait_confirm_text='wait_confirm'
#         wait_receive_text ='wait_receive'
#         cancel_num_text='cancel_num'

#         confirm ='confirmed'
#         cancel = 'cancel'
#         receive =0
#         wait_confirm=0
#         wait_receive =0
#         cancel_num=0
#         all_item =[]
#         print(status,'status')
#         if status:
#             print(code)
#             print(status)   
#             order = Order.objects.get(ref_code=code)
#             if order:
#                 order.confirm = status 
#                 order.save()
#                 if status =='confirmed':
#                     user = order.user
#                     print(user,'usernanafsdfs')
#                     message_confirmed(order,user)
#                 print(order.confirm,'save done')
#                 return redirect('confirm_order')

#         for order in orders:
#             print(len(orders))
#             list_item=[]
#             list_status=''
#             member_list = []
#             member = Member.objects.get(user=order.user)
#             print(order.confirm ,'confirmmmm')
#             if order.confirm == 'wait_to_confirm':
#                 wait_confirm +=1
#                 list_status='รอการยืนยัน'
#             elif order.confirm == 'confirmed' and order.completed == 'incompleted':
#                 wait_receive +=1
#                 list_status='รอดำเนินการ'
#             elif order.completed =='completed':
#                 receive +=1
#                 list_status='รับอาหารเเล้ว'
#             elif order.confirm == 'cancel':
#                 cancel_num +=1
#                 list_status='ยกเลิก'

#             order_items_type1 = OrderItemtype1.objects.filter(order=order)

#             for item in order_items_type1:
#                 list_item.append(item)

#             order_items_type2 = OrderItemtype2.objects.filter(order=order)
#             for item in order_items_type2:
#                 list_item.append(item)

#             all_item.append((order,time,list_item,list_status,member))
#             print(list_item)
#         print('receive',receive,'wait_confirm',wait_confirm,'wait_receive',wait_receive,'cancel_num',cancel_num,'me')
#     else:
#         if status:
#             print(code)
#             print(status)   
#             member_list=[]
#             reason = request.POST.get('select_reason')
#             print(reason)
#             order = Order.objects.get(ref_code=code)
#             if order:
#                 order.confirm = status 
#                 order.cancel_reason = reason
#                 order.save()
#                 user = order.user
#                 admin= Member.objects.get(pk=1)
#                 print(admin)
#                 message_cancel(order,user,admin)
#                 print(order.confirm,'save done')
#                 return redirect('confirm_order')
#     context={
#         'order':orders,
#         'confirm':confirm,
#         'cancel':cancel,
#         'all_item':all_item,
#         'len_order':len(orders),
#         'receive':receive,
#         'wait_confirm':wait_confirm,
#         'wait_receive':wait_receive,
#         'cancel_num':cancel_num,
#         'thai_date':thai_date,
#         'current_date':current_date,
#         'reason':reason,
#         'receive_filter':receive_text,
#         'wait_confirm_filter':wait_confirm_text,
#         'wait_receive_filter':wait_receive_text,
#         'cancel_filter':cancel_num_text,
#         'member':member_list,
#     }
#     return render(request, 'app/confirm_order.html', context)
@method_decorator(login_required, name='dispatch')    
class AdminConfirmOrderView(View):
    def get(self, request, code=None, status=None, filter=None):
        if not is_superuser(request.user):
            messages.error(request, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
            return redirect('home') 
        current_date = getdate()
        thai_date = getdate(None, current_date)
        current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
        orders = Order.objects.filter(created_at__contains=current_date, checkout=True)
        if filter:
            orders = filter_history_confirm(orders, filter)
        reason = CancelReason.objects.filter(use_with='admin')
        time = TimeReceive.objects.all()
        receive_text = 'receive'
        wait_confirm_text = 'wait_confirm'
        wait_receive_text = 'wait_receive'
        cancel_num_text = 'cancel_num'
        confirm = 'confirmed'
        cancel = 'cancel'
        receive = 0
        wait_confirm = 0
        wait_receive = 0
        cancel_num = 0
        all_item = []
        if status:
            order = get_object_or_404(Order, ref_code=code)
            if order:
                order.confirm = status
                order.save()
                if status == 'confirmed':
                    user = order.user
                    message_confirmed(order, user)
                return redirect('confirm_order')
        for order in orders:
            list_item = []
            list_status = ''
            member_list = []
            member = Member.objects.get(user=order.user)
            if order.confirm == 'wait_to_confirm':
                wait_confirm += 1
                list_status = 'รอการยืนยัน'
            elif order.confirm == 'confirmed' and order.completed == 'incompleted':
                wait_receive += 1
                list_status = 'รอดำเนินการ'
            elif order.completed == 'completed':
                receive += 1
                list_status = 'รับอาหารแล้ว'
            elif order.confirm == 'cancel':
                cancel_num += 1
                list_status = 'ยกเลิก'
            order_items_type1 = OrderItemtype1.objects.filter(order=order)
            for item in order_items_type1:
                list_item.append(item)
            order_items_type2 = OrderItemtype2.objects.filter(order=order)
            for item in order_items_type2:
                list_item.append(item)
            print(list_status)
            all_item.append((order, time, list_item, list_status, member))
        context = { 'order': orders, 'confirm': confirm,'cancel': cancel,
            'all_item': all_item, 'len_order': len(orders),'receive': receive,
            'wait_confirm': wait_confirm,'wait_receive': wait_receive,'cancel_num': cancel_num,
            'thai_date': thai_date,'current_date': current_date,'reason': reason,
            'receive_filter': receive_text,'wait_confirm_filter': wait_confirm_text,
            'wait_receive_filter': wait_receive_text,'cancel_filter': cancel_num_text,
            'member': member_list,}
        return render(request, 'app/confirm_order.html', context)
    
    def post(self, request, code=None, status=None, filter=None):
        if not is_superuser(request.user):
            messages.error(request, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
            return redirect('home')
        if status:
            reason = request.POST.get('select_reason')
            order = get_object_or_404(Order, ref_code=code)
            if order:
                order.confirm = status
                order.cancel_reason = reason
                order.save()
                user = order.user
                admin = Member.objects.get(pk=1)
                message_cancel(order, user, admin)
                return redirect('confirm_order')
        return redirect('confirm_order')  

@login_required           
def complete_order(req,ref_code):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    order = Order.objects.get(ref_code=ref_code)
    order_item1 = OrderItemtype1.objects.filter(order=order)
    order_item2 = OrderItemtype2.objects.filter(order=order)
    transaction = create_transaction(order_item1,order_item2)
    order.completed = 'completed'
    order.save()
    user = order.user
    message_complete(order,user)
    print(order)
    return redirect('confirm_order')

         
def filter_history_confirm(orders,filter):
        if filter =='receive':
            sort = orders.annotate(
            receive=Case(When(completed='completed', then=Value(0)),default=Value(1))).order_by('receive')
        elif filter =='wait_confirm':
            sort = orders.annotate(
            wait_confirm=Case(When(confirm='wait_to_confirm', then=Value(0)),default=Value(1))).order_by('wait_confirm')
        elif filter =='wait_receive':
            sort = orders.annotate(
            wait_receive=Case(When(confirm='confirmed',completed='incompleted', then=Value(0)),default=Value(1))).order_by('wait_receive')
        elif filter =='cancel_num':
            sort = orders.annotate(
            cancel_num=Case(When(confirm='cancel', then=Value(0)),default=Value(1))).order_by('cancel_num')
        return sort

@login_required           
def history_confirm_order(request,date=None,filter=None):
        if not is_superuser(request.user):
            messages.error(request, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
            return redirect('home') 
    # order = Order.objects.get(pk=order_id)
        if not date:
            print('not date')
            current_date = getdate()
            current_date = datetime.strptime(current_date, '%Y-%m-%d').date()

            date_filter = f'{current_date.year}-0{current_date.month}'
        else:
            date_filter =date
        orders = Order.objects.filter(created_at__contains=date_filter)
        if filter :
            orders = filter_history_confirm(orders,filter)

        date_raw = f'{date_filter}-01'
        thai_date = getdate(None,date_raw)
        print(thai_date[2:])
        confirm ='confirmed'
        cancel = 'cancel'

        receive_text ='receive'
        wait_confirm_text='wait_confirm'
        wait_receive_text ='wait_receive'
        cancel_num_text='cancel_num'

        receive =0
        wait_confirm=0
        wait_receive =0
        cancel_num=0

        all_item =[]
        if orders.exists():
            time = TimeReceive.objects.all()
            for order in orders:
                print(len(orders))
                list_item=[]
                list_status=''
                if order.confirm == 'wait_to_confirm':
                    wait_confirm +=1
                    list_status='รอการยืนยัน'
                elif order.confirm == 'confirmed' and order.completed == 'incompleted':
                    wait_receive +=1
                    list_status='รอดำเนินการ'
                elif order.completed =='completed' and order.confirm !='cancel':
                    receive +=1
                    list_status='รับอาหารเเล้ว'
                elif order.confirm == 'cancel':
                    cancel_num +=1
                    list_status='ยกเลิก'

                order_items_type1 = OrderItemtype1.objects.filter(order=order)

                for item in order_items_type1:
                    list_item.append(item)

                order_items_type2 = OrderItemtype2.objects.filter(order=order)
                for item in order_items_type2:
                    list_item.append(item)

                all_item.append((order,time,list_item,list_status))
                print(list_item)
            print('receive',receive,'wait_confirm',wait_confirm,'wait_receive',wait_receive,'cancel_num',cancel_num)
            print(date_filter)

        if request.method=='POST':
            date = request.POST.get('move_to_month') + '-01'
            print('date ==',date)
            if date:
                d = datetime.strptime(date, '%Y-%m-%d').date()
                print('move to',d)
                year = d.year
                month = d.month
                if month >9:
                    date = f'{year}-{month}'
                else:
                    date = f'{year}-0{month}'

                print(date)
                return redirect('confirm_order_admin', date=date)

        context={
                'order':orders,
                'confirm':confirm,
                'cancel':cancel,
                'all_item':all_item,
                'len_order':len(orders),
                'receive':receive,
                'wait_confirm':wait_confirm,
                'wait_receive':wait_receive,
                'cancel_num':cancel_num,
                'thai_date':thai_date[2:],
                'date_filter':date_filter,
                'receive_text' :receive_text,
                'wait_confirm_text':wait_confirm_text,
                'wait_receive_text' :wait_receive_text,
                'cancel_num_text':cancel_num_text,
        }
        return render(request, 'app/history_confirm_order.html', context)

@login_required           
def my_order(req):
    user = req.user
    current_date = getdate()
    current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
    date_filter = f'{current_date.year}-{current_date.month:02d}-{current_date.day:02d}'
    orders = Order.objects.filter(user=user,created_at__contains=date_filter,completed='incompleted',checkout=True).order_by('-created_at')
    if orders :
        time_test = TimeReceive.objects.all()
        reason_test = CancelReason.objects.filter(use_with='user')
        items = []
        for order in orders:
            order_items = []
            order_items_type1 = OrderItemtype1.objects.filter(order=order)
            for item in order_items_type1:
                order_items.append(item)
            order_items_type2 = OrderItemtype2.objects.filter(order=order)
            for item in order_items_type2:
                order_items.append(item)
            thai_tz = pytz.timezone('Asia/Bangkok')
            thai_time = timezone.localtime(order.created_at, timezone=thai_tz)
            date_raw = order.created_at.date()
            date = getdate(None,str(date_raw))
            date = f'{date} เวลา {thai_time.strftime("%H:%M")} น.'
            items.append(( order,order_items,date))
        context ={
                    'order':orders,
                    'items':items,
                    'time':time_test,
                    'reason':reason_test,}
    else:
        context ={
                    'order':orders,}
    return render(req,'app/my_order.html',context)

@login_required           
def cancel_my_order(req,ref_code):
    order = Order.objects.get(ref_code=ref_code)
    reason = req.POST.get('select_reason')
    order.confirm = 'cancel'
    order.cancel_reason = reason
    order.save()
    user = order.user
    message_cancel(order,user)
    return redirect('my_order')

# @login_required           
# def my_history(req,filter=None):
#     wait = 'wait'
#     receive ='receive'
#     cancel = 'cancel'
#     completed = 'completed'
#     orders =''
#     if not filter:
#         orders = Order.objects.filter(user=req.user,checkout=True).order_by('-created_at')
#     else:
#         if filter =='wait':
#             orders = Order.objects.filter(user=req.user, checkout=True).annotate(wait_order=Case(
#                 When(confirm='wait_to_confirm', then=Value(0)),default=Value(1))).order_by('wait_order', '-created_at')
#             if not orders:
#                 orders=None
#         elif filter =='receive':
#             orders = Order.objects.filter(user=req.user,checkout=True).annotate(
#             confirmed_order=Case(When(confirm='confirmed', then=Value(0)),default=Value(1))).order_by('confirmed_order','-created_at')
#             if not orders:
#                 orders=None
#         elif filter =='cancel':
#             orders = Order.objects.filter(user=req.user,checkout=True).annotate(
#             cancel_order=Case(When(confirm='cancel', then=Value(0)),default=Value(1))).order_by('cancel_order','-created_at')
#             if not orders:
#                 orders=None
#         elif filter == 'completed':
#             orders = Order.objects.filter(user=req.user,checkout=True).annotate(
#             completed_order=Case(When(completed='completed', then=Value(0)),default=Value(1))).order_by('completed_order','-created_at')
#             if not orders:
#                 orders=None
#     if orders :
#         time = TimeReceive.objects.all()
#         items = []
#         for order in orders:
#             order_items = []
#             total_price = 0
#             order_items_type1 = OrderItemtype1.objects.filter(order=order)
#             for item in order_items_type1:
#                 order_items.append(item)
#                 total_price += item.total_price
#             order_items_type2 = OrderItemtype2.objects.filter(order=order)
#             for item in order_items_type2:
#                 order_items.append(item)
#                 total_price += item.total_price
#             thai_tz = pytz.timezone('Asia/Bangkok')
#             thai_time = timezone.localtime(order.created_at, timezone=thai_tz)
#             date_raw = order.created_at.date()
#             date = getdate(None,str(date_raw))
#             date = f'{date} เวลา {thai_time.strftime("%H:%M")} น.'
#             items.append(( order,order_items,date,total_price))
#         context ={
#                     'order':orders,
#                     'items':items,
#                     'time':time,
#                     'receive':receive,
#                     'wait':wait,
#                     'cancel':cancel,
#                     'completed':completed, }
#     else:
#         context ={
#                     'order':orders,
#                     'receive':receive,
#                     'wait':wait,
#                     'cancel':cancel}
#     return render(req,'app/history_order.html',context)
@method_decorator(login_required, name='dispatch')
class MyHistoryView(View):
    def get(self, req, filter=None, *args, **kwargs):
        wait = 'wait'
        receive = 'receive'
        cancel = 'cancel'
        completed = 'completed'
        orders = ''
        if not filter:
            orders = Order.objects.filter(user=req.user, checkout=True).order_by('-created_at')
        else:
            if filter == 'wait':
                orders = Order.objects.filter(user=req.user, checkout=True).annotate(
                    wait_order=Case(When(confirm='wait_to_confirm', then=Value(0)), default=Value(1))
                ).order_by('wait_order', '-created_at')
                if not orders:
                    orders = None
            elif filter == 'receive':
                orders = Order.objects.filter(user=req.user, checkout=True).annotate(
                    confirmed_order=Case(When(confirm='confirmed', then=Value(0)), default=Value(1))
                ).order_by('confirmed_order', '-created_at')
                if not orders:
                    orders = None
            elif filter == 'cancel':
                orders = Order.objects.filter(user=req.user, checkout=True).annotate(
                    cancel_order=Case(When(confirm='cancel', then=Value(0)), default=Value(1))
                ).order_by('cancel_order', '-created_at')
                if not orders:
                    orders = None
            elif filter == 'completed':
                orders = Order.objects.filter(user=req.user, checkout=True).annotate(
                    completed_order=Case(When(completed='completed', then=Value(0)), default=Value(1))
                ).order_by('completed_order', '-created_at')
                if not orders:
                    orders = None
        if orders:
            time = TimeReceive.objects.all()
            items = []
            for order in orders:
                order_items = []
                total_price = 0
                order_items_type1 = OrderItemtype1.objects.filter(order=order)
                for item in order_items_type1:
                    order_items.append(item)
                    total_price += item.total_price
                order_items_type2 = OrderItemtype2.objects.filter(order=order)
                for item in order_items_type2:
                    order_items.append(item)
                    total_price += item.total_price
                thai_tz = pytz.timezone('Asia/Bangkok')
                thai_time = timezone.localtime(order.created_at, timezone=thai_tz)
                date_raw = order.created_at.date()
                date = getdate(None, str(date_raw))
                date = f'{date} เวลา {thai_time.strftime("%H:%M")} น.'
                items.append((order, order_items, date, total_price))
            context = {
                'order': orders,'items': items,'time': time,
                'receive': receive, 'wait': wait,'cancel': cancel,
                'completed': completed,}
        else:
            context = {
                'order': orders,'receive': receive,'wait': wait,'cancel': cancel,}
        return render(req, 'app/history_order.html', context)
    
def qr_code(req,check=None):
    if check:
        return render(req,'app/qr_code.html',context={'check':check})
    return render(req,'app/qr_code.html')

def next_qr_code(req):
    user = req.user
    messages.error(req,'กรุณากรอบข้อมูลส่วนตัวให้ครบถ้วน')
    return redirect('profile',username=user)

@login_required           
def recommend_us(req):
    if req.method == 'POST':
        form = RecommendForm(req.POST, req.FILES)
        text = req.POST.get('text')
        form.instance.text = text
        if form.is_valid():
            member = Member.objects.get(user=req.user)
            form.instance.user = member
            form.save()  
            return redirect('home')
    else:
        form = RecommendForm() 

    context = {
        'form': form
    }
    return render(req, 'app/recommend.html', context)

@login_required           
def show_recommend(req):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    rec = RecommendUs.objects.all()
    return render(req,'app/show_recom.html',context={
        'recomend':rec})

@login_required           
def full_recommend(req,id):
    if not is_superuser(req.user):
        messages.error(req, "ท่านไม่มีสิทธิเข้าถึงหน้านี้")
        return redirect('home') 
    rec = RecommendUs.objects.get(pk=id)
    return render(req,'app/show_full_rec.html',context={
        'recomend':rec})
