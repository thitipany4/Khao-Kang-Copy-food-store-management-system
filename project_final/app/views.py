from collections import defaultdict
import requests
from django.shortcuts import get_object_or_404, redirect, render
from app.forms import *
#from linebot import LineBotApi
#from linebot.models import TextSendMessage
from app.models import *
from django.contrib.auth.models import User
import folium
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .line_login import LineLogin

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
                f.options = 'soldout'
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
            review.owner = member

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
        food_ids = req.POST.getlist('food_id')
        print(food_ids)
        options = req.POST.getlist('options')
        print(options)
        if len(food_ids) == len(options):
            for id, option in zip(food_ids, options):
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
                    if Historysale.objects.filter(food_id=food_item.id, date_field=date).exists():
                        if food_item.options != option:
                            food_item.options = option
                            food_item.save()
                            print('เปลี่ยนแปลงข้อมูลสำเร็จ (Data changed successfully)')
                        else:
                            print('ไม่มีการเปลี่ยนแปลง (No changes made)')
                    else:
                        food_item.options = option
                        food_item.save()
                        history_sale = Historysale.objects.create(food=food_item, date_field=date)
                        print('เซฟข้อมูลลงฐานข้อมูลได้ (Saved data to the database)')

        return redirect('managefood')
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