from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'quantity']

class ProductForm2(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity']

class OrderConfirmationForm(forms.Form):
    confirm = forms.BooleanField(required=True)

