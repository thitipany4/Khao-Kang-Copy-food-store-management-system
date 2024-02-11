from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
import requests
from django.shortcuts import get_object_or_404, redirect, render
from app.forms import *
#from linebot import LineBotApi
#from linebot.models import TextSendMessage
from app.models import *
from django.contrib.auth.models import User
from django.db import transaction
import folium
from itertools import zip_longest
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .generate_code import generate_random_system_code
from .clear_session import *
from .line_login import LineLogin
from .calculator import calculator
from .forms import FormNote
from .utils import EventCalendar

def getdate(x=None,th=None):
    '''
    get_month = thai_month_dict[current_date.month]
    formatted_date = f"{current_date.year}-{get_month}-{current_date.day}"
    date = datetime.strptime(formatted_date, '%Y-%m-%d').date()
    '''
    #เพื่อ เอาวันที่แบบตัวหนังสือ ปี-เดือน-วัน
    if x:
        current_date = x
        print(current_date,'xxxxxxxxxx')
        return f'{current_date.year}-{current_date.month}-{current_date.day}'
    

    
    #เพื่อ เอาวันที่แบบตัวหนังสือ แบบไทย 4 ธันวาคม 2023
    else:
        if th:
            date = th
            current_date = datetime.strptime(date, '%Y-%m-%d').date()
            print(current_date,'yyyyyyyyyyyyyy')
    
        else:
            current_date = datetime.now()
            print(current_date,'ppppppppppppppppp')
            return f'{current_date.year}-{current_date.month}-{current_date.day}'

        thai_month_dict = {
        1:"มกราคม",
        2:"กุมภาพันธ์",
        3:"มีนาคม",
        4:"เมษายน",
        5:"พฤษภาคม",
        6:"มิถุนายน",
        7:"กรกฎาคม",
        8:"สิงหาคม",
        9:"กันยายน",
        10:"ตุลาคม",
        11:"พฤศจิกายน",
        12:"ธันวาคม",}
        get_month = thai_month_dict[current_date.month]
        return f'{current_date.day} {get_month} {current_date.year}'

#------------------------------------------------------------------

# Create your views here.

def home(req):
    t = Transaction.objects.all()
    for d in t:
        print('tran id',d.id)
    #key = check()
    food = Food.objects.all()
    context ={
        'food':food,
    }
    return render(req,'app/home.html',context)
def about_us(req):
    map = folium.Map(location=[15.268875,104.8260654],zoom_start=12)
    us =(15.279417,104.831893)
    folium.Marker(us).add_to(map)
    context = {
        'map':map._repr_html_()
    }
    return render(req,'app/aboutus.html',context)
def create(req):
    form = FoodForm()
    if req.method =='POST':
        form = FoodForm(req.POST,req.FILES)
        if form.is_valid():
            form.save()
            return redirect('managefood')
    context = {
        'form':form
    }
    return render(req,'app/create.html',context)

def search(req):
    if req.method =='POST':
        text = req.POST['text-search']
        if text:
            food = Food.objects.filter(name__contains=text)
            if food:
                return render(req,'app/search.html',{'food':food})
            else:
                return render(req,'app/search.html',{'text':'ไม่พบเมนูอาหารที่ท่านค้นหา'}) 
        else:
            return render(req,'app/search.html',{'text':'กรุณาเพิ่มเมนูอาหารที่ท่านต้องการค้นหา'}) 

        
    else:
        return render(req,'app/search.html',{'text':'กรุณาเพิ่มเมนูอาหารที่ท่านต้องการค้นหา'}) 

def select_date(req):
    if req.method =='POST':
            form_date = DateForm(req.POST)

            if form_date.is_valid():
                date = form_date.cleaned_data['date_field']
                print(date)
                get_date = getdate(date)
                print('get_date:',get_date)
                currect_date = getdate(datetime.now().date())
                print('currect_date:',currect_date)
                #ทำการเปรียบเทียบ ถ้าวันที่ ที่ส่งมาเป็นเมื่อวานหรือมากกว่านั้น ให้ รีเทิร์น history.html ไป แต่ ถ้าเป็นปัจจุบันก็รีเทิร์น managefood.html
                # currect_date > get_date = เมื่อวาน
                if currect_date > get_date:

                    food_history = Historysale.objects.filter(date_field=get_date)
                    foods = []
                    for history in food_history:
                        if history.food:
                            foods.append(history.food)
                    print(foods)
                    form_date = DateForm()
                    thai_date = getdate(None,get_date)
                    print(thai_date)
                    context ={
                        'date':get_date,
                        'thai_date':thai_date,
                        'food':foods,
                        'form':form_date,
                    }
                    return render(req,'app/historysales.html',context)
                # currect_date < get_date = เมื่อวาน
                elif currect_date < get_date:
                    food_history = Historysale.objects.filter(date_field=get_date)
                    foods = []
                    for history in food_history:
                        if history.food:
                            foods.append(history.food)
                    print(foods)
                    form_date = DateForm()
                    thai_date = getdate(None,get_date)
                    print(thai_date)

                    context ={
                        'date':get_date,
                        'thai_date':thai_date,
                        'food':foods,
                        'form':form_date,
                        
                        
                    }
                    return render(req,'app/historysales.html',context)
                # present
                else:
                   print('44444444444444')
                   return redirect('/managefood/')
    else:
            food = Food.objects.all()
            form_date = DateForm()
            get_date = getdate()
            thai_date = getdate(None,get_date)


    context ={
        'date':get_date,
        'thai_date':thai_date,
        'food':food,
        'form':form_date,

    }
    return render(req,'app/managefood.html',context)

def clearfood(req):
    if req.method=='POST':
        #Food.objects.exclude(options='notchoose').update(options='notchoose')
        food = Food.objects.all()
        for f in food:
            if f.options != 'notchoose':
                print('setsetset')
                print(f)
                f.options = 'notchoose'
                f.save()
        return redirect('managefood')
    else:
        return redirect('managefood')
def updatefood(req,id):
    if req.method=='GET':
        food = Food.objects.get(pk=id)
        form = FoodForm(instance=food)
    else:
        food = Food.objects.get(pk=id)
        form = FoodForm(req.POST,req.FILES,instance=food)
        if form.is_valid():
            form.save()
            return redirect('managefood')
    context ={
        'food':food,
        'form':form,
    }
    return render(req,'app/updatefood.html',context)

def profile(req,username):
    if req.method=='GET':
        user =  get_object_or_404(User,username=username)
        member = Member.objects.get(user=user)
        form = MemberForm(instance=member)
    else:
        user =  get_object_or_404(User,username=username)
        member = Member.objects.get(user=user)
        form = MemberForm(req.POST,req.FILES,instance=member)
        if form.is_valid():
            form.instance.age = req.POST.get('age')
            form.save()
            print(form.instance.age)
            return redirect('home')
        else:
            print(form.errors)
            print(form.non_field_errors)
    context ={
        'member':member,
        'form':form,
    }
    return render(req,'app/profile.html',context)
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
        for i in review:
            print(i.owner)
        orderby =review.order_by('-created')
        star_range = [1,2,3,4,5]
        # print(review)
        print('...........................................................................................')
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


        # Now, organize the data for stars and their counts
        ratings = []
        for i in range(1, 6):
            rating_count = star_count[i]
            width = (rating_count / count_score) * 100 if count_score > 0 else 0
            ratings.append({'rating': i, 'count': rating_count, 'width': width})

        for i in ratings:
            print('rating :',i)
        
        if req.method == "GET" and target:
            if target == 'lastest':
                orderby = review.order_by('-created')
                print('date')
                print(orderby)
                
            else:
                orderby = review.order_by('-rating')
                print('best')

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

def reviewfood(req,id):
    food = Food.objects.get(pk=id)
    if req.method =='GET':
        form = ReviewFood(instance=food)
        print(form.instance.id)
    else:
        print('suscess')
        form = ReviewFood(req.POST,req.FILES)
        form.instance.food = food


        if form.is_valid():
            review = form.save(commit=False)
            member = Member.objects.get(user=req.user)
            print(form.instance.rating)
            review.owner = member
            food.quantity_review +=1
            if food.quantity_review !=0:
                average_score = (food.score * (int(food.quantity_review) - 1) + form.instance.rating) / food.quantity_review
                food.score = round(average_score, 2)
                food.score = average_score
            food.save()
            review.save()
            return redirect('home')
        else:
            print(form.errors)
            print(form.non_field_errors)
    context = {
        'form':form,
        'food':food,
    }
    return render(req,'app/review.html',context)


def managefood(req, date=None):
    print(date)
    if req.method == 'POST':
        quantity = req.POST.getlist('input_quantity')
        print(quantity)
        food_ids = req.POST.getlist('food_id')
        print(food_ids)
        options = req.POST.getlist('options')
        print(options)
        if len(food_ids) == len(options):
            for id, option,quantity in zip(food_ids, options,quantity):
                food_item = Food.objects.get(pk=id)
                print(food_item, f'pass {option}')
                if option == 'notchoose':
                    found = Historysale.objects.filter(food_id=food_item.id, date_field=date)
                    print(found)
                    if found.exists():
                        food_item.options = option
                        food_item.save()
                        found.delete()
                        print('ลบสำเร็จ (Deletion successful)')
                    else:
                        print('ไม่พบข้อมูลในฐานข้อมูล (Data not found in the database)')

                elif option in ['onsale', 'soldout']:
                    found = Historysale.objects.filter(food_id=food_item.id, date_field=date).first()
                    if found:
                        if food_item.options != option:
                            food_item.options = option
                            found.quantity = quantity
                            food_item.quantity_sale = quantity
                            found.save()
                            food_item.save()
                            print('เปลี่ยนแปลงข้อมูลสำเร็จ (Data changed successfully)')
                        else:
                            print('ไม่มีการเปลี่ยนแปลง (No changes made)')
                            if quantity:
                                found.quantity = quantity
                                food_item.quantity_sale = quantity
                                found.save()
                                food_item.save()
                    else:
                        food_item.options = option
                        food_item.quantity_sale = quantity
                        food_item.save()
                        history_sale = Historysale.objects.create(food=food_item, date_field=date,quantity=quantity)

                        print('เซฟข้อมูลลงฐานข้อมูลได้ (Saved data to the database)')
                

        return redirect('managefood')
    else:
        food = Food.objects.all()
        form_date = DateForm()
        get_date = getdate()
        thai_date = getdate(None,get_date)
        history = Historysale.objects.filter(date_field=get_date)
        list_food =[]

        for food in food:
            found_item = ''
            print(food)
            for item in history:
                if food == item.food:
                    found_item = item
                    break
            if found_item:
                list_food.append((food,found_item))
            else:
                list_food.append((food,''))
        print(list_food)

        context ={
            'date':get_date,
            'thai_date':thai_date,
            'food':food,
            'form':form_date,
            'list_food':list_food,
        }
        return render(req,'app/managefood.html',context)



def login(req):
      if req.user.is_authenticated:
          print('success login..........................................................')
      return render(req,'app/login.html')

def line_login(request):
    line = LineLogin()
    auth_link = line.get_link()  # Get the authorization link

    return redirect(auth_link)
 
def line_callback(request):
    if 'code' in request.GET and 'state' in request.GET:
        code = request.GET['code']
        state = request.GET['state']

        line = LineLogin()
        token = line.token(code, state)

        if token.get('error'):
            return redirect('managefood')

        if token.get('id_token'):
            profile = line.profile_from_id_token(token)
            request.session['profile'] = profile

            # Retrieve user information or create a new user
            # Replace this logic with your Django User and Member models

            user_id = profile.get('name')  # Assuming 'email' is used as user_id
            user = User.objects.filter(username=user_id).first()
            print(user)
            print('user_id',user_id)

            if user:
                    auth_login(request, user)
                    return redirect('home') 
            else:
                print('you in else')
                line_user = request.user if request.user.is_authenticated else User.objects.create_user(username=user_id)
                line_user_profile, created = Member.objects.get_or_create(
                    #id =profile['user_id'],
                    user=line_user,
                    email=profile['email'],
                    picture=profile['picture'],
                    # Add other fields you want to populate in Member model
                )
                print('register success')
                # Optionally redirect to home or another page
            user = authenticate(request, username=user_id, password=None)
            print('user:',user)
            if user is not None:
                    # Log the user in
                    auth_login(request, user)
                    return redirect('home') 

    # Handle cases where 'code' or 'state' is not in the request.GET
    return redirect('home')  # Redirect to a suitable page

def logout(req):
    auth_logout(req)
    return redirect('home')

def send_line_message(req):
    pass
'''
def line_login(req):
      print('------------------------------------------------------------')
      line_login_url = 'https://access.line.me/oauth2/v2.1/login?returnUri=%2Foauth2%2Fv2.1%2Fauthorize%2Fconsent%3Fclient_id%3D2002071461%26redirect_uri%3Dhttp%253A%252F%252F127.0.0.1%253A8000%252Flogin%252Fcallback%252F%26scope%3Dprofile%2Bopenid%2Bemail%26response_type%3Dcode%26state%3Do5LbuxfoP3E5zU3p&loginChannelId=2002071461&loginState=5RSv0jsdBZgXGfTdkjcF0u'
      return redirect(line_login_url)


def get_line_user_info(access_token):
    user_info_url = 'https://api.line.me/v2/profile'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(user_info_url, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        user_id = user_data.get('userId')
        display_name = user_data.get('displayName')
        email = user_data.get('email', '')
        picture = user_data.get('pictureUrl', '')
        openid = user_data.get('openid')

        return {
            'user_id': user_id,
            'display_name': display_name,
            'email': email,
            'picture': picture,
            'openid': openid
        }
    else:
        print('Failed to fetch user information.')
        return None


def line_callback(req):

    if req.method == 'GET':
        # Extract the callback data from the request
        callback_data = req.GET.dict()

        # Check if 'code' is in the callback data
        if 'code' in callback_data:
            authorization_code = callback_data['code']
            access_token_url = 'https://api.line.me/oauth2/v2.1/token'
            payload = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': 'http://127.0.0.1:8000/login/callback/',
                'client_id': '2002071461',
                'client_secret': 'ccdce5af4dca9056f145c473d7193d11'
            }

            # Send a POST request to exchange authorization code for an access token
            response = requests .post(access_token_url, data=payload)

            if response.status_code == 200:
                access_token_data = response.json()
                access_token = access_token_data.get('access_token')
                # Now, you can use the access_token to make requests to Line API to get user information
                # e.g., Get user profile information

                # Replace the below with your logic to handle the access_token and fetch user info
                print('Access Token:', access_token)
                user_info = get_line_user_info(access_token)
                print('User ID:', user_info['user_id'],type(user_info['user_id']))
                if user_info:
                     user = User.objects.get(username=user_info['user_id'])
                     if user !=[]:
                        
                        # member = Member.objects.get(user=user)
                        auth_login(req, user)
                        return redirect('home') 
                        # return render(req,'app/home.html',{'member':member})
                     else:
                        line_user = req.user if req.user.is_authenticated else User.objects.create_user(username=user_info['user_id'])
                        line_user_profile, created = Member.objects.get_or_create(
                                user=line_user,
                                user_name = user_info['display_name'],)
                        user = User.objects.get(username=user_info['user_id'])
                        if user !=[]:
                            return render(req,'app/login.html',)


    # Access other user-related data as needed
                return redirect('home')
            else:
                print('Failed to retrieve access token.')
                return redirect('error_page')  # Redirect to an error page or handle as needed
        else:
            print('Authorization code not found in callback data.')
            return redirect('error_page')  # Redirect to an error page or handle as needed
'''
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

def calendar(req,date=None,mark=None):
    my_calendar = EventCalendar()
    if req.method == 'GET':
        if date and mark =='next_month':
            d = datetime.strptime(date, '%Y-%m-%d').date()
            date_str = get_next_month(d)
            date=getdate(date_str)
            print('date11',date_str)
        elif date and mark =='prev_month':
            print('date  dd' ,date)
            d = datetime.strptime(date, '%Y-%m-%d').date()
            date_str = get_prev_month(d)
            date=getdate(date_str)
            print('date11',date_str)
        else:
            date = getdate()
            print('currect month')
            date_str = datetime.strptime(date, '%Y-%m-%d').date()
        
        print('rrrrrrr',date_str)
        year = date_str.year
        month = date_str.month
        calendar_html = my_calendar.formatmonth(year, month)
    else:
        date = req.POST.get('move_to_month') + '-01'
        print('date ==',date)
        if date:
            d = datetime.strptime(date, '%Y-%m-%d').date()
            print('move to',d)
            year = d.year
            month = d.month
            calendar_html = my_calendar.formatmonth(year, month)
            note = Transaction.objects.filter(date__year=year, date__month=month)
            # print(note)
            sum_expenses,sum_income= calculator(note)
            total = sum_income- sum_expenses 
            context = {'calendar_html': calendar_html,
                        'date':date,
                        'total':total,
                        'sum_expenses':sum_expenses,
                        'sum_income':sum_income,}
            return render(req, 'app/calendar_template.html',context)
        else:
            print('วันที่ภายในฟอร์มไม่ได้เลือก')
            return redirect('home')

    note = Transaction.objects.filter(date__year=date_str.year, date__month=date_str.month)
    # print(note)
    sum_expenses,sum_income= calculator(note)
    total = sum_income- sum_expenses 
    context = {'calendar_html': calendar_html,
                'date':date,
                'total':total,
                'sum_expenses':sum_expenses,
                'sum_income':sum_income,}
    return render(req, 'app/calendar_template.html',context)

def note(req, date=None):
    print(date)
    expenses = 'expenses'
    income ='income'
    form = FormNote()
    if req.method =='POST':
        name_values = req.POST.getlist('name')
        price_values = req.POST.getlist('price')
        amount_values = req.POST.getlist('amount')
        transaction_type_values = req.POST.getlist('transaction')
        print('namesssss :', name_values)
        print('namesssss :', price_values)
        print('namesssss :', amount_values)


        for i in range(len(name_values)):
            if name_values[i] == '':
                continue
            else:
                check = Transaction.objects.filter(name=name_values[i],date=date).first()
                print('check',check)
                if check:
                    if check.name !=name_values[i] or check.price !=price_values[i] or check.amount !=amount_values[i]:
                        form = FormNote({'name': name_values[i],
                                         'price': price_values[i],
                                         'amount': amount_values[i],},
                                         req.POST,instance=check)
                        if form.is_valid():
                            form.save()
                        print('data are duplicate')
                else:
                    print('transaction_type ', [i], transaction_type_values[i])
                    form = FormNote({
                        'name': name_values[i],
                        'price': price_values[i],
                        'amount': amount_values[i],
                    }, req.FILES)

                    if form.is_valid():
                        # Process form data and save to the database
                        form.instance.date = date
                        form.instance.transaction_type = transaction_type_values[i]
                        form.save()
                        print('form save success')
            print('save round',[i])
        print('redirect home')
        return redirect('calendar')
    else:
        tran = Transaction.objects.filter(date=date)
        if tran.exists():
            print('have tran')
            list_income = []
            list_expenses =[]
            list_leftover =[]
            for t in tran:
                if t.transaction_type == 'expenses':
                    list_expenses.append(t)
                    print(t,t.transaction_type)
                    print('list_expenses',list_expenses)
                elif t.transaction_type == 'income':
                    list_income.append(t)
                    print(t,t.transaction_type)
                    print('list_income',list_income)
                else:
                    list_leftover.append(t)
                    print(t,t.transaction_type)
                    print('list_leftover',list_leftover)

            tem = '''
                        <div class="container-add-form" id="forms-container-leftover">
                            <form method="post" class="add-leftover" action="/note/{{date}}/" enctype="multipart/form-data">
                                {%csrf_token%}

                                <input  class="bar-str" type="text" name="name" step="any" required id="id_name">

                                <input  class="bar-price" type="text" name="price" step="any" required id="id_price">

                                <input  class="bar-amount" type="text" name="amount" step="any" required id="id_amount">

                                <input type="hidden" name="transaction" value="leftover">

                                <!-- <select name="options" id="transaction_type">
                                    <option value="expenses">expenses</option>
                                    <option value="income">income</option>
                                </select> -->

                                <button type="button" class="delete-button" onclick="deleteForm(this)">Delete</button>

                            </form>
            
                        </div>
                '''

            context ={
                'form':form,
                'date':date,
                'tran':tran,
                'expenses':expenses,
                'income':income,
                'list_expenses':list_expenses,
                'list_income':list_income,
                'list_leftover':list_leftover,
                'tem':tem,
            }
            return render(req,'app/view_form.html', context)
        else:
            print('dont have tran')
            context ={
                'form':form,
                'date':date,
                'expenses':expenses,
                'income':income,
            }
            return render(req,'app/view_form.html', context)

     
def show_note(req,date=None):
    note = Transaction.objects.filter(date=date)
    sum_expenses,sum_income,list_expenses,list_income,list_leftover= calculator(note,'show_note')
    total = sum_income- sum_expenses 
    print(total)
    context = {
         'list_income':list_income,
         'list_expenses':list_expenses,
         'list_leftover':list_leftover,
         'sum_expenses':sum_expenses,
         'sum_income':sum_income,
         'total':total,
         'date':date,
    }
    return render(req, 'app/show-note.html',context )
def delete_note(request,note_id,date):
    note = get_object_or_404(Transaction, pk=note_id,date=date)
    print(note , 'delete done')
    if note:
        note.delete()
        return redirect('show-note',date=date)

    else:
        return redirect('show-note',date=date)



def create_cart(request):
    existing_order = Order.objects.filter(user=request.user,checkout=False).first()
    if existing_order and existing_order.checkout !=True :
        order = existing_order
        print(order)
        return redirect('view_cart')
    else:
        random_code = generate_random_system_code()
        order = Order.objects.create(total_price=Decimal('0.00'), ref_code=random_code,user=request.user)
        request.session['order'] = order.ref_code  # Use ref_code for session
        print(order, 'create cart done')
    return render(request, 'app/view_cart.html', {'order': order})

def view_cart(request):
    order_id = request.session.get('order')

    if order_id:
        order = get_object_or_404(Order, ref_code=order_id)
        order_item1 = OrderItemtype1.objects.filter(order=order)
        order_item2 = OrderItemtype2.objects.filter(order=order)
        type_1 = 'type1'
        type_2 = 'type2'
        context ={
            'order':order,
            'order_item1':order_item1,
            'order_item2':order_item2,
            'type_1':type_1,
            'type_2':type_2,
        }
    return render(request, 'app/view_cart.html', context)

def delete_cart(request,code):
    # order_id = request.session.get('order')
    # pop_order_id = request.session.pop('order', None)
    request.session.pop('cart', None)
    print('order id',code)
    if id:
        Order.objects.filter(ref_code=code).delete()
        print('deleted cart')
    return redirect('home')

def shopping_food_type1(request):
    foods = Food.objects.all()
    return render(request, 'app/shop_food1.html', {'food': foods,
                                                         })
def modify_cart1(request):
    foods = Food.objects.all()
    items = OrderItemtype1.objects.all()
    food_item = []
    for food in foods:
        found_item = ''
        print(food)
        for item in items:
            if food == item.food:
                found_item = item
                break
        if found_item:
            food_item.append((food,found_item))
        else:
            food_item.append((food,0))
    modify = 'True'
        
    return render(request, 'app/shop_food1.html', {'food_item': food_item, 'modify':modify
                                                         })

def shopping_food_type2(request,id=None):
    foods = Food.objects.all()
    # form = ProductForm2()
    return render(request, 'app/shop_food2.html', {'food': foods,
                                                         })
def modify_cart2(request,id):
    special = 'False'
    foods = Food.objects.all()
    item = OrderItemtype2.objects.get(pk=id)
    if item.price == 50:
        special = 'True'
    modify = f'{item.id}'
    selected = []
    print('modify2',item)
    for i in item.foods.all():
        selected.append(i.id)
    print(selected)
    return render(request, 'app/shop_food2.html', {'food': foods, 'selected':selected,'modify':modify,'special':special,'item':item,
                                                         })
def add_to_cart(request,type,modify=None):
    if request.method == 'POST':
        
        if type=='type1':
            print('type1')
            product_ids = request.POST.getlist('product_id')
            print('product_ids',product_ids)

            quantities = request.POST.getlist('quantity')
            print('quantities',quantities)
            cart = request.session.get('cart', [])
            order_id = request.session.get('order')
            print('order_id',order_id)
            
            for product_id, quantity in zip(product_ids, quantities):
                print('in loop')
                print('product_id', product_id)
                print('quantity',quantity)
                product = get_object_or_404(Food, pk=product_id)
                print('product', product)
                quantity = int(quantity)  # Convert quantity to an integer
    
                if quantity == 0:  # Check if the current quantity is 'delete'
                    product = OrderItemtype1.objects.filter(food=product,user=request.user)
                    order = get_object_or_404(Order, ref_code=order_id)
                    if product.exists():
                        if order:
                            item = product.first()
                            order.total_price -= (item.food.price*item.quantity)
                        order.save()
                        product.delete()
                        print(item,'has beend delete ')
                        continue
                    else:
                        print('not data deleted')
                        continue
                    

                
                print(quantity,'ppp')
                # Check if the product is already in the cart
                existing_item = next((item for item in cart if item['id'] == product.id), None)
                print('existing_item', existing_item)

                if existing_item:
                    print('updating existing item')
                    # Update quantity if the product is already in the cart
                    existing_item['quantity'] += quantity
                else:
                    # Add a new item to the cart
                    cart.append({'id': product.id, 'name': product.name, 'price': str(product.price), 'quantity': quantity,'type':'type1'})
                    print('cart', cart)

                # Update order data in the database
                if not order_id:
                    print('creating new order')
                    random_code = generate_random_system_code()
                    order = Order.objects.create(total_price=Decimal('0.00'), ref_code=random_code, user=request.user)
                    print('created success')
                    request.session['order'] = random_code
                else:
                    print('using existing order')
                    order = get_object_or_404(Order, ref_code=order_id)

                order_item, created = OrderItemtype1.objects.get_or_create(order=order,user=request.user, food=product,
                                                                       defaults={'quantity': 0, 'price': product.price})
                if not modify :
                    order_item.quantity += quantity
                    order.total_price += (product.price * quantity)
                else:
                    if order_item.quantity != quantity:
                        order.total_price -= (product.price*order_item.quantity)
                        order.total_price += (product.price * quantity)
                        order_item.quantity = quantity
                    else:
                        print('it is same')
                order_item.save()
                order.save()

            request.session['cart'] = cart
            print('.................')
            print(cart)
            return redirect('shopping_food1')

        else:
            print('start type 2')
            product_ids = request.POST.getlist('product_id')
            quantities = request.POST.getlist('quantity')
            checked_add = request.POST.getlist('add_to_cart')
            special = request.POST.get('special')
            order_id = request.session.get('order')
            print('special',special)
         
            selected_product_ids = [product_id for product_id, checked in zip(product_ids, checked_add) if checked == 'checked']
            selected_products = Food.objects.filter(id__in=selected_product_ids)
            print('selected_products', selected_products)
            
            cart = request.session.get('cart', [])
            total_quantity = sum(int(quantity) for quantity in quantities)
            print(total_quantity)
            if selected_products:
                with transaction.atomic():
                    if not order_id:
                        random_code = generate_random_system_code()
                        order = Order.objects.create(total_price=Decimal('0.00'), ref_code=random_code,user=request.user)
                        request.session['order'] = order.id
                    else:
                        order = get_object_or_404(Order, ref_code=order_id)
                    if modify:
                        id =int(modify)
                        order_item = OrderItemtype2.objects.get(pk=id)
                        print('get item',order_item)
                    else:
                        order_item = OrderItemtype2.objects.create(order=order, user=request.user, quantity=total_quantity, price=0)
                    if total_quantity == 0 :
                        print('order price',order.total_price)
                        print((order_item.price))
                        print((order_item.quantity))

                        order.total_price -= (order_item.price*order_item.quantity)
                        print('order price',order.total_price)
                        order_item.delete()
                        order.save()
                        print('orderitem2 have been delete')
                        return redirect('view_cart')
                    
                    food_names = ' + '.join(product.name for product in selected_products)

                    order_item.name = food_names
                    print('order_item.name',order_item.name)

                    order_item.foods.set(selected_products)
                    print('order_item.foods',order_item.foods)
                    # if not special:
                    #     order_item.price = 40
   
                    print(food_names)
                    if not modify :
                        if special == 'not checked':
                            order_item.price = 40
                        else:
                            order_item.price = 50
                        print(order_item.price)
                        print('order_item', order_item)
                        order_item.quantity = total_quantity
                        order.total_price += (order_item.price * total_quantity)
                        print('order price ',order.total_price)
                        print('order itemmm',order_item)
                        
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
                        print(order_item.price)
                        print('order_item', order_item)
                        
                        if order_item.quantity != total_quantity:
                            if original_price:
                                order.total_price -= (original_price*order_item.quantity)
                                order.total_price += (order_item.price*order_item.quantity)

                            order.total_price -= (order_item.price*order_item.quantity)
                            order_item.quantity = total_quantity
                            print('order_item quantity ',order_item.quantity)
                            order.total_price += (order_item.price*order_item.quantity)
                            print('order price ',order.total_price)


                        else:
                            if original_price:
                                order.total_price -= (original_price*order_item.quantity)
                                order.total_price += (order_item.price*order_item.quantity)         
                            print('it is same')
                        
                    order_item.save()
                    order.save()

                        # Include order_item data in the cart
                    cart_item = {
                            'id': order_item.id,
                            'name': food_names,
                            'price': str(order_item.price),
                            'quantity': total_quantity,
                            'type': 'type2',
                        }

                    print(cart_item)
                    existing_item = next((item for item in cart if item['id'] == order_item.id), None)
                    if existing_item:
                            existing_item['quantity'] += total_quantity
                    else:
                            cart.append(cart_item)

                    request.session['cart'] = cart

                return redirect('view_cart')
            
def delete_from_cart(request, product_id,type):
    if type == 'type1':
        product = get_object_or_404(OrderItemtype1, pk=product_id,user=request.user) # ปัญหาที่ database เพราะมันเป็น object เดียวกัน ต้องแยก
        print(product , 'delete done')

    else:
        product = get_object_or_404(OrderItemtype2, id=product_id,user=request.user) # ปัญหาที่ database เพราะมันเป็น object เดียวกัน ต้องแยก
        print(product , 'delete done')

    order = product.order
    with transaction.atomic():
        order.total_price -= product.price * product.quantity
        order.save()

        # Delete the order item
        product.delete()

    # Retrieve the current cart from the session
    cart = request.session.get('cart', [])

    # Remove the product from the cart if it exists
    cart = [item for item in cart if item['id'] != product_id]

    # Update the session with the modified cart
    request.session['cart'] = cart

    # Redirect back to the cart view
    return redirect('view_cart')

def checkout(request):
    order_id = request.session.get('order')
    if order_id:
        order = get_object_or_404(Order, ref_code=order_id)
        order_item1 = OrderItemtype1.objects.filter(order=order)
        order_item2 = OrderItemtype2.objects.filter(order=order)
        context ={
            'order':order,
            'order_item1':order_item1,
            'order_item2':order_item2,

        }
        return render(request, 'app/checkout.html', context)
    else:
        return redirect('view_cart')
def get_quatity(obj):
    date = getdate()
    food_sale = get_object_or_404(Historysale,food=obj,date_field=date)
    return food_sale
def order_confirmation(request, order_id=None):
    if order_id is None:
        order_id = request.session.pop('order', None)
        return redirect('home')

    if order_id:
        order = get_object_or_404(Order, ref_code=order_id)
        order_item1 = OrderItemtype1.objects.filter(order=order)
        order_item2 = OrderItemtype2.objects.filter(order=order)
        if order_item1:
            for i in order_item1:
                food = Food.objects.filter(pk=i.food.id).first()
                food_sale = get_quatity(food)
                food_sale.quantity -= i.quantity 
                food_sale.save()
                print(i.quantity)
                print(food_sale.quantity)
        if order_item2:
            for item in order_item2:
                for i in item.foods.all():
                    print(i,'iii')
                    foods = get_object_or_404(Food,pk=i.id)
                    food_sale2 = get_quatity(foods)
                    food_sale2.quantity -= item.quantity
                    food_sale.save()
                    print('food_sale2.quantity',food_sale2.quantity)
        print(order_item2.first().foods.all())
        request.session.pop('order', None)
        request.session.pop('cart', None)
        order.checkout = True
        order.save()
        print('order has been checkout')
        context ={  
            'order':order,
            'order_item1':order_item1,
            'order_item2':order_item2,

        }
        return render(request, 'app/order_confirmation.html', context)
    else:
        return redirect('product_list')

def confirm_order(request,code=None,status=None):
    # order = Order.objects.get(pk=order_id)
    if request.method == 'GET':
        orders = Order.objects.all().order_by('-created_at')
        confirm ='confirmed'
        cancel = 'cancel'
        if status:
            print(code)
            print(status)   
            order = Order.objects.get(ref_code=code)
            if order:
                order.confirm = status 
                order.save()
                print(order.confirm,'save done')
                return redirect('confirm_order')

    context={
        'order':orders,
        'confirm':confirm,
        'cancel':cancel
    }
    return render(request, 'app/confirm_order.html', context)