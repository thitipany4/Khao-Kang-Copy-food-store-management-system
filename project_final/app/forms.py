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
class DateForm(forms.ModelForm):
    class Meta:
        model = Historysale
        fields = ['date_field']
        widgets = {
            'date_field': forms.DateInput(attrs={'type': 'date'})
        }

class OptionForm(forms.ModelForm):
    class Meta:
        model = Food
        fields =['options']

class ReviewFood(forms.ModelForm):
    class Meta:
        model = Reviewfood
        fields ="__all__"