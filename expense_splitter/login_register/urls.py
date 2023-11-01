from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('home/', views.home, name="home"),
    path('getLogin/', views.getLogin, name="getLogin"),
    path('login/', views.login, name="login"),
    # path('getRegister/', views.getRegister, name="getRegister"),
    path('register/', views.register, name="register"),
    # path('logout/', views.logout, name="logout"),
    # path('home/', views.home, name="home"),
    # path('secret/', views.secret, name="secret"),
]