from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from .models import UserProfile, Activity, Join, Msg
from django.utils import timezone
from django.contrib import messages

from .forms import ActivityForm

# modified by Stone Stone


@login_required
def user_info(request):
    user_profile = UserProfile.find_user_by_id(UserProfile(), request.user.id)[1]
    return render(request, 'user_info.html', {'user_profile': user_profile})

@login_required
def show_user_info(request,user_id):
    user_profile = UserProfile.find_user_by_id(UserProfile(), user_id)[1]
    return render(request, 'user_info.html', {'user_profile': user_profile})