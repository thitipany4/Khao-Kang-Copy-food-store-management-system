from datetime import datetime
from django.db import models
from PIL import Image
from django.contrib.auth.models import User
# Create your models here.
#class Member(models.Model):
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    email =models.EmailField(blank=True,null=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    phone_number = models.CharField(max_length=100)
    picture = models.URLField(blank=True, null=True)
    age = models.CharField(max_length=20, choices=(
        ('11-20', '11-20 ปี'),
        ('21-30', '21-30 ปี'),
        ('31-40', '31-40 ปี'),
        ('41-50', '41-50 ปี'),
        ('51-60', '51-60 ปี'),
        ('60+', '60 ปีขึ้น'),
    ), default='11-20') 
    gender = models.CharField(max_length=20, choices=(
        ('Male', 'ผู้ชาย'),
        ('Female', 'ผู้หญิง'),
        ('Other', 'อื่นๆ'),

    ), default='11-20') 
    def __str__(self) -> str:
        return f'{self.user_name} '
class Food(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    unit = models.CharField(max_length=100,default='บาทต่อถุง')
    score = models.FloatField(default=0,blank=True,null=True)
    quantity_review = models.IntegerField(default=0,blank=True,null=True)
    image = models.ImageField(upload_to='media/image/',blank=True,null=True)
    options = models.CharField(max_length=20, choices=(
        ('notchoose', 'ไม่ได้เลือก'),
        ('onsale', 'วางขาย'),
        ('soldout', 'ขายหมดแล้ว'),
    ), default='notchoose') 


    def __str__(self) -> str:
        return f'เมนู {self.name} ราคา {self.price} บาท status : {self.options}'
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
    food = models.ForeignKey(Food,on_delete=models.DO_NOTHING,null=True,blank=True)

    def __str__(self) -> str:
        return f'{self.date_field} {self.food}'
    
class Reviewfood(models.Model):
    food = models.ForeignKey(Food,on_delete=models.CASCADE)
    review = models.TextField(max_length=500,blank=True,null=True)
    rating = models.CharField(max_length=20, choices=(
        ('1', '1 ดาว'),
        ('2', '2 ดาว'),
        ('3', '3 ดาว'),
        ('4', '4 ดาว'),
        ('5', '5 ดาว'),

    ), default='5',blank=False,null=False) 

    def __str__(self) -> str:
        return f'{self.food.name} rating : {self.rating}'

