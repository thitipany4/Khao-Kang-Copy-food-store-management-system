from datetime import date, datetime
from django.db import models
from PIL import Image
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time
import pytz

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email =models.EmailField(blank=True,null=True)
    first_name = models.CharField(max_length=100,blank=True,null=True)
    last_name = models.CharField(max_length=100,blank=True,null=True)
    line_id = models.CharField(max_length=100,blank=True,null=True)
    phone_number = models.CharField(max_length=100)
    picture = models.URLField(blank=True, null=True)
    age = models.CharField(max_length=20, choices=(
        ('11-20 ปี', '11-20 ปี'),
        ('21-30 ปี', '21-30 ปี'),
        ('31-40 ปี', '31-40 ปี'),
        ('41-50 ปี', '41-50 ปี'),
        ('51-60 ปี', '51-60 ปี'),
        ('60 ปีขึ้น', '60 ปีขึ้น'),
    ), default='11-20') 
    gender = models.CharField(max_length=20, choices=(
        ('Male', 'ผู้ชาย'),
        ('Female', 'ผู้หญิง'),
        ('Other', 'อื่นๆ'),

    ), default='11-20') 
    def __str__(self) -> str:
        return f'{self.user} {self.email} '
    
class Food(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    unit = models.CharField(max_length=100,default='บาทต่อถุง')
    score = models.FloatField(default=0,blank=True,null=True)
    quantity_review = models.IntegerField(default=0,blank=True,null=True)
    # quantity_sale = models.IntegerField(default=0)
    image = models.ImageField(upload_to='media/image/',blank=True,null=True)

    def __str__(self) -> str:
        return f'เมนู {self.name} ราคา {self.price} บาท '
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            if img.height >300 or img.width >300:
                output_size = (300,300)
                img.thumbnail(output_size)
                img.save(self.image.path)
            
        
    
class Historysale(models.Model):
    date_field = models.DateField()
    food = models.ForeignKey(Food,on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.IntegerField(default=0)
    OPTIONS = [
        ('ไม่ได้เลือก', 'ไม่ได้เลือก'),
        ('วางขาย', 'วางขาย'),
        ('ขายหมดแล้ว', 'ขายหมดแล้ว'),
    ]
    options = models.CharField(max_length=20, choices=OPTIONS,null=True) 
    def __str__(self) -> str:
        return f'{self.date_field} {self.food.name}'
    
    @classmethod
    def update_options_at_2pm(cls):
        current_time = timezone.now().time()
        if current_time == time(12, 0):  # 14:00 is 2 pm
            
            cls.objects.update(options=None)

class Reviewfood(models.Model):
    food = models.ForeignKey(Food,on_delete=models.CASCADE)
    owner = models.ForeignKey(Member,on_delete=models.CASCADE,null=True)
    review = models.TextField(max_length=500,blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(choices=(
        (1, '1 ดาว'),
        (2, '2 ดาว'),
        (3, '3 ดาว'),
        (4, '4 ดาว'),
        (5, '5 ดาว'),

    ), default=5) 

    def __str__(self) -> str:
        return f'{self.food.name} rating : {self.rating}'

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('expenses', 'expenses'),
        ('income', 'income'),
        ('leftover','Leftover')
    ]
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=0.0)
    amount = models.IntegerField(default=0)
    total_price =models.IntegerField(default=0)
    date = models.DateField(null=True,blank=True)
    created = models.DateTimeField(default=timezone.now)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)


    def __str__(self) -> str:
        return f'{self.name} {self.date}'

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(null=True)  # Remove auto_now_add=True
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    ref_code = models.CharField(max_length=100, null=True)
    checkout = models.BooleanField(default=False)
    TIME_CHOICES = [
        ('10:00 AM', '10:00 น.'),
        ('10:30 AM', '10:30 น.'),
        ('11:00 AM', '11:00 น.'),
        ('11:30 AM', '11:30 น.'),
        ('12:00 PM', '12:00 น.'),
        ('12:30 PM', '12:30 น.'),
        ('01:00 PM', '13:00 น.'),
        ('01:30 PM', '13:30 น.'),
    ]
    REASON = [
        ('soldout','สินค้าหมด'),
        ('cant-call-user','ไม่สามารถติดต่อลูกค้าได้'),
        ('user-dont-receive','ลูกค้าไม่มารับอาหาร'),
        ('user-cancel','ลูกค้าเปลี่ยนใจ/ยกเลิกการจอง'),
        ('cant-receive','ไม่สามารถไปรับอาหารได้'),
    ]
    time_receive = models.CharField(max_length=20, choices=TIME_CHOICES, null=True)
    confirm = models.CharField(max_length=20, choices=(
        ('wait_to_confirm', 'รอยืนยัน'),
        ('confirmed', 'ยืนยันเเล้ว'),
        ('cancel', 'ยกเลิก'),
    ), default='wait_to_confirm')
    completed = models.CharField(max_length=20, choices=(
        ('incompleted', 'ยังไม่สมบุรณ์'),
        ('completed', 'สมบุรณ์'),
    ), default='incompleted')
    cancel_reason = models.CharField(max_length=40, choices=REASON,null=True,blank=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            thai_tz = pytz.timezone('Asia/Bangkok')
            utc_now = timezone.now()
            self.created_at = utc_now.astimezone(thai_tz)
        super().save(*args, **kwargs)
        
    def __str__(self) -> str:
        return f'{self.ref_code} confirm {self.confirm}'
class OrderItemtype1(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food = models.ForeignKey(Food,on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f'{self.food} price {self.total_price}'
    
class OrderItemtype2(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=True)
    foods = models.ManyToManyField('Food')
    quantity = models.IntegerField()
    price = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f'{self.name} price {self.total_price}'