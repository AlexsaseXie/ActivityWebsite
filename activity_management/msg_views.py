from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from .models import UserProfile, Activity, Join, Msg
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
import datetime

from .forms import ActivityForm,DateForm,MessageForm,ActivitySearchForm

@login_required
def send_message(request):
    if (request.method == 'POST'):
        form = MessageForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            receive_user_name = cd['receive_user_name']
            title = cd['title']
            content = cd['content']
            receive_user_id = UserProfile.get_user_id(UserProfile(), receive_user_name)
            Msg.create_msg(Msg(), request.user, receive_user_id, title, content)
    form = MessageForm()
    return render(request, 'send_message.html', {'form': form})

@login_required
def unread_message(request):
    msgs = Msg.find_all_msgs(Msg(), request.user.id)
    return render(request, 'unread_message.html',{'msgs' : msgs})

@login_required
def delete_message(request,msg_id):
    Msg.remove_msg(Msg(), msg_id)
    msgs = Msg.find_all_msgs(Msg(), request.user.id)
    return render(request, 'unread_message.html',{'msgs' : msgs})

@login_required
def delete_all_messages(request):
    msgs = Msg.find_all_msgs(Msg(), request.user.id)
    for msg in msgs:
        Msg.remove_msg(Msg(), msg.id)
    msgs = []
    return render(request, 'unread_message.html', {'msgs': msgs})

@login_required
def set_read(request,msg_id):
    Msg.set_msg_read(Msg(), msg_id)
    msgs = Msg.find_all_msgs(Msg(), request.user.id)
    return render(request, 'unread_message.html', {'msgs': msgs})

@login_required
def set_all_read(request):
    msgs = Msg.find_all_msgs(Msg(), request.user.id)
    for msg in msgs:
        Msg.set_msg_read(Msg(), msg.id)
    msgs = Msg.find_all_msgs(Msg(), request.user.id)
    return render(request, 'unread_message.html', {'msgs': msgs})

@login_required
def reply_message(request,msg_id):
    msg = Msg.find_msg(Msg(), msg_id)
    username = msg.from_user_id.username
    form = MessageForm(initial={'receive_user_name' : username})
    return render(request, 'send_message.html', {'form': form})

@login_required
def send_to_Ta(request,user_id):
    username = UserProfile.find_user_by_id(UserProfile(),user_id)[0].username
    form = MessageForm(initial={'receive_user_name' : username})
    return render(request, 'send_message.html', {'form': form})