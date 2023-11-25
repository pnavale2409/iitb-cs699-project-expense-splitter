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

# Create your views here.
@login_required(login_url='/login/')
def home(request):
    # Retrieve user data from the database
    user_groups = Group.objects.filter(groupmember__member=request.user)
    
    # Check if the user is a member of any groups
    if user_groups.exists():
        user_memberships = User.objects.filter(groupmember__group__in=user_groups)
        
        # Pass user data to the template
        context = {
            'user_groups': user_groups,
            'user_memberships': user_memberships,
        }

        # Fetch all groups for the groups_list
        

        return render(request, 'home.html', context)
    else:
        # If the user is not a member of any groups, handle it accordingly
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
            return redirect('/login')  # Replace 'home' with the URL name for your home page
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

        # Check if the group with the same name already exists
        existing_group = Group.objects.filter(name=group_name).first()
        if existing_group:
            messages.error(request, f'A group with the name "{group_name}" already exists.')
            return redirect('/')

        group = Group(name=group_name)
        group.save()
       
        # Add the current user as a member of the group
        GroupMember.objects.create(group=group, member=request.user)

        messages.success(request, f'The group "{group_name}" has been created successfully.')
        return redirect('/')  # Replace 'home' with the name of your home view
    else:
       
        form = CreateGroupForm()

    return render(request, 'home.html', {'form': form})

@login_required
def group_details(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group_members = GroupMember.objects.filter(group=group)
    expenses = Expense.objects.filter(group=group)

     # Calculate total expense and user share
    total_expense = expenses.aggregate(total_expense=models.Sum('amount'))['total_expense'] or 0
    user_share = total_expense / len(group_members) if len(group_members) > 0 else 0

    # Calculate how much the current user owes or is owed
    user_expenses = expenses.filter(payer=request.user)
    user_total_expense = user_expenses.aggregate(total_expense=models.Sum('amount'))['total_expense'] or 0
    user_balance = user_total_expense - user_share

    # Fetch expenses with payer names
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

                # Assuming you have a ForeignKey from Expense to Group
                expense = Expense(description=description, amount=amount, group=group, payer=request.user)
                expense.save()

                messages.success(request, 'Expense added successfully.')
                return redirect('/')

            except Group.DoesNotExist:
                messages.error(request, 'Group does not exist.')
                return redirect('/')

            return redirect('/')

    else:
        expense_form = ExpenseForm()

    context = {
        'user_groups': user_groups,
        'expense_form': expense_form,
    }

    return render(request, 'home.html')

@login_required
def add_member(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        username = request.POST.get('username', '')

        try:
            user_to_add = User.objects.get(username=username)

            # Check if the user is not already a member of the group
            if not GroupMember.objects.filter(group=group, member=user_to_add).exists():
                # Create a new GroupMember instance to associate the user with the group
                GroupMember.objects.create(group=group, member=user_to_add)
                messages.success(request, f'{user_to_add.username} added to the group.')
            else:
                messages.warning(request, f'{user_to_add.username} is already a member of the group.')

        except User.DoesNotExist:
            messages.error(request, f'User with username {username} does not exist.')

    return redirect('group_details', group_id=group.id)