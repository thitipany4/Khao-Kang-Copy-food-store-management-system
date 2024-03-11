from django.shortcuts import render
from django_plotly_dash.views import add_to_session
from .app import app
# Create your views here.
def home(req):
    add_to_session(req,app)
    print(app)
    return render(req,'dashboard/home.html',{
        'app':app
    })