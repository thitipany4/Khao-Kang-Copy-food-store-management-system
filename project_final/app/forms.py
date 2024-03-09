from django import forms

from app.models import *


class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = [
            'name',
            'price',
            'unit',
            'image',
        ]
class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields =[
            'first_name',
            'last_name',
            'phone_number',
            'age'
        ]
class DateForm(forms.ModelForm):
    class Meta:
        model = Historysale
        fields = ['date_field']
        widgets = {
            'date_field': forms.DateInput(attrs={'type': 'date'})
        }


class ReviewFood(forms.ModelForm):
    class Meta:
        model = Reviewfood
        fields =[
            'review',
            'rating',
        ]
class FormNote(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'name',
            'price',
            'amount',

        ]
class OrderItemtype1Form(forms.ModelForm):
    class Meta:
        model = OrderItemtype1
        fields = [ 'order', 'food', 'quantity', 'total_price']