from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    select = models.BooleanField(default=False)

    def __str__(self):
        return self.name
class Order(models.Model):
    #user = models.fogrekey(User,,,,,)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    confirmed = models.BooleanField(default=False)
    ref_code = models.CharField(max_length=100,null=True)
    def __str__(self) -> str:
        return f'{self.ref_code} corfirmed {self.confirmed}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    products = models.ManyToManyField('Product')
    name= models.CharField(max_length=100,null=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

#ดู งง สร้างเป็น 2 ตัวเลยน่าจะง่ายกว่า oderitem