from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User,Group,auth
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def home(request):
    return render(request,'home.html')

def getLogin(request):
    return render(request,'login.html')

def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(username=username,password=password)

    if (user is not None):
        auth.login(request,user)
        return redirect('/home')       
    else:
        return HttpResponse("Invalid login credentials")

def getRegister(request):
    return render(request,'register.html')

def register(request):
    if request.method == 'POST':
        # form = UserCreationForm(request.POST)
        user_data = request.POST.dict()
        username = user_data.get("username")
        f_name = user_data.get("f_name")
        l_name = user_data.get("l_name")
        email = user_data.get("email")
        password = user_data.get("password")
        user = User.objects.create_user(username, email,password)
        user.first_name = f_name
        user.last_name = l_name
        user.save()
            # Log in the user after registration
            # login(request, user)
        return redirect('/getLogin')  # Replace 'home' with the URL name for your home page
    else:
        form = UserCreationForm()
    return render(request, 'register.html')


# def home(request):
#     return render(request,'home.html')

# def logout(request):
#     auth.logout(request)
#     return redirect('/')

# @login_required(login_url='/getLoginPage/')
# def secret(request):
#     return render(request, 'secret.html')