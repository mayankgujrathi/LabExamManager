from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from .models import StudentProfile


import re

User = get_user_model()
PIN_REGEX = re.compile(r'[0-9]{5,6}-[a-zA-z]{1,3}-[0-9]{3,5}')

def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('admins-home')
    login_form = AuthenticationForm()
    if request.method == 'POST':
        login_form = AuthenticationForm(request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome Back {username}!')
                # setting pc's name for user
                if hasattr(user, 'student_profile'):
                    user.student_profile.hostname = request.POST.get('hostname')
                    user.student_profile.save()
                elif hasattr(user, 'admin_profile'):
                    user.admin_profile.hostname = request.POST.get('hostname')
                    user.admin_profile.save()
                return redirect('admins-home')
            else:
                messages.error(request, 'Invalid Username or Password!')
        else:
            messages.error(request, 'Invalid Username or Password!')
    return render(request, 'users/login.html', {'title': 'Sign in Page','form': login_form})

@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.info(request, 'You are now signed out!')
    return redirect('users-login')

def register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('admins-home')
    if request.method == 'POST' and request.POST:
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            if not PIN_REGEX.search(form.cleaned_data.get('username')):
                messages.error(request, 'Invalid PIN, your username is the PIN field')
                return render(request, 'users/register.html', {'title': 'Sign Up Page','form': form})
            form.save()
            user = User.objects.get(username=form.cleaned_data.get('username'))
            obj = StudentProfile(user=user)
            obj.save()
            messages.success(request, f'{form.cleaned_data.get("username")} account created!')
            return redirect('users-login')
        else:
            messages.error(request, 'Unable to Sign Up!')
    form = UserRegisterForm()
    return render(request, 'users/register.html', {'title': 'Sign Up Page','form': form})