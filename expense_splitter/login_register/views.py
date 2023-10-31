from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User,Group,auth
from django.contrib.auth.decorators import login_required, permission_required


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
    
# def home(request):
#     return render(request,'home.html')

# def logout(request):
#     auth.logout(request)
#     return redirect('/')

# @login_required(login_url='/getLoginPage/')
# def secret(request):
#     return render(request, 'secret.html')