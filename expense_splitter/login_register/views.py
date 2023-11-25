# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User,Group,auth
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request,'home.html')

def login(request):
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username,password=password)
        if (user is not None):
            auth.login(request,user)
            return redirect('/')
           
        else:
            messages.info(request,'Invalid Credentials')
            return redirect('login')       
    else:
        return render(request,'login.html')



def register(request):
    if request.method == 'POST':
        # form = UserCreationForm(request.POST)
        user_data = request.POST.dict()
        username = user_data.get("username")
        f_name = user_data.get("f_name")
        l_name = user_data.get("l_name")
        email = user_data.get("email")
        password = user_data.get("password")

        if User.objects.filter(username=username).exists():
            messages.info(request,'Username Taken')
            return redirect('register') 
        elif User.objects.filter(email=email).exists():
            messages.info('Email Taken')
            return redirect('register')
        else:
            user = User.objects.create_user(username=username, password=password, email=email, first_name = f_name, last_name=l_name)
            user.save()
            print('User created')
            # Log in the user after registration
            # login(request, user)
            return redirect('/getLogin')  # Replace 'home' with the URL name for your home page
    else:
        form = UserCreationForm()
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('/')