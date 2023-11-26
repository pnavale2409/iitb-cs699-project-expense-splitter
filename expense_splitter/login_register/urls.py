from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('logout',views.logout, name="logout"),
    path('create_group/',views.create_group, name="create_group"),
    path('group/<int:group_id>/', views.group_details, name='group_details'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('group/<int:group_id>/add_member/', views.add_member, name='add_expense'),
    path('group/<int:group_id>/remove_expense/<int:expense_id>/', views.remove_expense, name='remove_expense'),
]