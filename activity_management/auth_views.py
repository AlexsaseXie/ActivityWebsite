from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from .models import UserProfile, Activity, Join, Msg


def sign_up(request):
    return render(request, 'sign_up.html')


def sign_up_submit(request):
    user_name = request.POST.get('username')
    password = request.POST.get('password')
    check_password = request.POST.get('check_password')
    email = request.POST.get('email')
    privilege = 0
    real_name = request.POST.get('real_name')

    uf = UserProfile()

    # examination
    if not password == check_password:
        #return redirect('sign_up')
        # or
        return HttpResponse('Require refused: Password not match.')

    if UserProfile.check_username_exist(uf, user_name):
        #return redirect('sign_up')
        # or
        return HttpResponse('Require refused: Username already registered.')

    # create user
    UserProfile.create_userprofile(uf, uname=user_name, password=password, real_name=real_name, email=email, privilege=privilege)
    return redirect('log_in')
        # or
        # return HttpResponse('Require refused.\nUnknown error.')


def log_in(request):
    return render(request, 'log_in.html')


def log_in_submit(request):
    user_name = request.POST.get('username')
    password = request.POST.get('password')

    # examination
    user = auth.authenticate(request, username=user_name, password=password)
    if not user:
        # return redirect('log_in')
        return HttpResponse('Require refused: Incorrect username or password.')

    auth.login(request, user)
    privilege = UserProfile.find_user_privilege(UserProfile(),request.user.id)
    if not privilege:
        return redirect('home')
    elif privilege < 2 :
        return redirect('home')
    else :
        return redirect('admin_home')


@login_required
def authenticate(request):
    return render(request, 'authenticate.html')


@login_required
def authenticate_submit(request):
    code = request.POST.get('auth_code')
    auth_code = 'AUTH'
    admin_code = 'ADMIN'

    auth_privilege = 1
    admin_privilege = 2

    if code == auth_code:
        UserProfile.change_user_privilege(UserProfile(), request.user.id, auth_privilege)
        return redirect('home')
        # return HttpResponse(str(request.user.id) + '  ' + str(request.user.username))
    elif code == admin_code:
        UserProfile.change_user_privilege(UserProfile(), request.user.id, admin_privilege)
        return redirect('home')
    else:
        return HttpResponse('Require refused: Incorrect code.')


@login_required
def log_out(request):
    auth.logout(request)
    return redirect('home')

