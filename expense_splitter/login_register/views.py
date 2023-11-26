# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Group, GroupMember, Expense
from django import forms
from django.db import models
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
import base64

matplotlib.use('Agg')


@login_required(login_url='/login/')
def home(request):
    
    user_groups = Group.objects.filter(groupmember__member=request.user)

    
    if user_groups.exists():
        user_memberships = User.objects.filter(groupmember__group__in=user_groups)
   
        user_expenses = Expense.objects.filter(payer=request.user)
       
        descriptions = [expense.description for expense in user_expenses]
        amounts = [expense.amount for expense in user_expenses]

        fig, ax = plt.subplots(figsize=(5.6, 5))

        ax.bar(descriptions, amounts,color='#4285f4')

        ax.set_xlabel('Expense Descriptions')
        ax.set_ylabel('Amount ($)')
        ax.set_title('User Expenses')

        img_data1 = BytesIO()
        plt.savefig(img_data1, format='png')
        plt.close()

        img_data1.seek(0)
        expense_plot = base64.b64encode(img_data1.getvalue()).decode()

        user_groups = Group.objects.filter(groupmember__member=request.user)

        group_names = []
        total_expenses = []

        for group in user_groups:
            group_total_expense = Expense.objects.filter(group=group, payer=request.user).aggregate(total_expense=models.Sum('amount'))['total_expense'] or 0
            group_names.append(group.name)
            total_expenses.append(group_total_expense)

        fig, ax = plt.subplots(figsize=(5.6, 5))

        ax.bar(group_names, total_expenses,color='yellow')

        ax.set_xlabel('Groups Names')
        ax.set_ylabel('Total Expenses ($)')
        ax.set_title('Total Expenses in Each Group')

        img_data2 = BytesIO()
        plt.savefig(img_data2, format='png')
        plt.close()

        img_data2.seek(0)
        group_expense_plot = base64.b64encode(img_data2.getvalue()).decode()

        user_groups = Group.objects.filter(groupmember__member=request.user)

        group_names = []
        balance = []

        for group in user_groups:
            group_members = GroupMember.objects.filter(group=group).count()
            user_total_expense = Expense.objects.filter(group=group, payer=request.user).aggregate(total_expense=models.Sum('amount'))['total_expense'] or 0
            total_expense = Expense.objects.filter(group=group).aggregate(total_expense=models.Sum('amount'))['total_expense'] or 0
            user_share = total_expense /group_members if group_members > 0 else 0
            user_balance=user_total_expense-user_share
            group_names.append(group.name)
            balance.append(user_balance)

        colors = ['green' if b >= 0 else 'red' for b in balance]

        fig, ax = plt.subplots(figsize=(5.6, 5))

        ax.bar(group_names, balance,color=colors)

        ax.set_xlabel('Group Names')
        ax.set_ylabel('Balance ($)')
        ax.set_title('User balance in Each Group')


        img_data3 = BytesIO()
        plt.savefig(img_data3, format='png')
        plt.close()

        img_data3.seek(0)
        balance_plot = base64.b64encode(img_data3.getvalue()).decode()

        context = {
            'user_groups': user_groups,
            'user_memberships': user_memberships,
            'expense_plot': expense_plot,
            'group_expense_plot':group_expense_plot,
            'balance_plot':balance_plot,
        }
        return render(request, 'home.html', context)
    else:
        return render(request, 'home.html')

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
            return redirect('/login')  
    else:
        form = UserCreationForm()
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

class CreateGroupForm(forms.Form):
    g_name = forms.CharField(max_length=255)

@login_required
def create_group(request):
    if request.method == 'POST':
        form_data = request.POST.dict()
        group_name = form_data.get('g_name')

        existing_group = Group.objects.filter(name=group_name).first()
        if existing_group:
            messages.error(request, f'A group with the name "{group_name}" already exists.')
            return redirect('/')

        group = Group(name=group_name)
        group.save()
       
        GroupMember.objects.create(group=group, member=request.user)

        messages.success(request, f'The group "{group_name}" has been created successfully.')
        return redirect('/') 
    else:
       
        form = CreateGroupForm()

    return render(request, 'home.html', {'form': form})

@login_required
def group_details(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group_members = GroupMember.objects.filter(group=group)
    expenses = Expense.objects.filter(group=group)

    total_expense = expenses.aggregate(total_expense=models.Sum('amount'))['total_expense'] or 0
    user_share = total_expense / len(group_members) if len(group_members) > 0 else 0

    user_expenses = expenses.filter(payer=request.user)
    user_total_expense = user_expenses.aggregate(total_expense=models.Sum('amount'))['total_expense'] or 0
    user_balance = user_total_expense - user_share

    expenses_with_payers = []
    for expense in expenses:
        payer_name = expense.payer.username
        expenses_with_payers.append({'expense': expense, 'payer_name': payer_name})

    context = {
        'group': group,
        'group_members': group_members,
        'total_expense': total_expense,
        'user_share': user_share,
        'user_balance': user_balance,
        'expenses_with_payers': expenses_with_payers,
    }

    return render(request, 'group_details.html', context)

@login_required
def add_expense(request):
    user_groups = Group.objects.filter(groupmember__member=request.user)

    class ExpenseForm(forms.Form):
        description = forms.CharField(max_length=255, required=True)
        amount = forms.DecimalField(required=True)
        group_name = forms.CharField(max_length=255, required=True)

    if request.method == 'POST':
        expense_form = ExpenseForm(request.POST)
        if expense_form.is_valid():
            description = expense_form.cleaned_data['description']
            amount = expense_form.cleaned_data['amount']
            group_name = expense_form.cleaned_data['group_name']

            try:
                group = Group.objects.get(name=group_name, groupmember__member=request.user)

                expense = Expense(description=description, amount=amount, group=group, payer=request.user)
                expense.save()

                messages.success(request, 'Expense added successfully.')
                return redirect('/')

            except Group.DoesNotExist:
                messages.error(request, 'Group does not exist.')
                return redirect('/')

            
    else:
        expense_form = ExpenseForm()

    return render(request, 'home.html')

@login_required
def add_member(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        username = request.POST.get('username', '')

        try:
            user_to_add = User.objects.get(username=username)

            if not GroupMember.objects.filter(group=group, member=user_to_add).exists():
                GroupMember.objects.create(group=group, member=user_to_add)
                messages.success(request, f'{user_to_add.username} added to the group.')
            else:
                messages.warning(request, f'{user_to_add.username} is already a member of the group.')

        except User.DoesNotExist:
            messages.error(request, f'User with username {username} does not exist.')

    return redirect('group_details', group_id=group.id)

def remove_expense(request, group_id, expense_id):
    group = get_object_or_404(Group, id=group_id)
    expense = get_object_or_404(Expense, id=expense_id)

    if request.user != expense.payer:
        messages.error(request, "You don't have permission to remove this expense.")
        return redirect('group_details', group_id=group.id)
    
    expense.delete()

    messages.success(request, 'Expense removed successfully.')
    return redirect('group_details', group_id=group.id)