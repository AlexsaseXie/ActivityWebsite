from django.contrib import auth
from .models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import models

#

def log_in(request):
    return render(request, 'login.html')

def sign_up(request):
    return render(request, 'signup.html')

def sign_up_submit(request):
    username = request.POST.get('username')

    User.objects.create_user()
    User.user_type()

@login_required
def log_out(request):
    auth.logout(request)
    return redirect('home')

@login_required
def authenticate(request):
    return render(request, 'auth.html')