from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from .models import UserProfile, Activity, Join, Msg
from django.utils import timezone
from django.contrib import messages

from .forms import ActivityForm


def show_user_info(request,user_id):
    user = UserProfile.find_user_by_id(UserProfile(), user_id)
    return render(request, 'user_info.html', {'user_obj': user[0], 'user_profile': user[1]})


@login_required
def change_info(request):
    return render(request, 'change_info.html')


@login_required
def change_info_submit(request):
    password = request.POST.get('password')
    check_password = request.POST.get('check_password')
    email = request.POST.get('email')
    real_name = request.POST.get('real_name')

    # examination
    if not password == check_password:
        # return redirect('sign_up')
        # or
        return HttpResponse('Require refused: Password not match.')

    # update
    UserProfile.update_user_info(UserProfile(), request.user.id, None, password, real_name, email)
    return redirect('home')
