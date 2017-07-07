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


#活动相关
def show_activity(request,activity_id):
    act = Activity.find_activity(Activity(),activity_id)
    return render(request, 'show_activity.html' ,{'activity':act,'joined': UserProfile.check_user_join_activity(UserProfile(),request.user.id,activity_id)})

@login_required
def apply_activity(request):
    privilege = UserProfile.find_user_privilege(UserProfile(),request.user.id)

    if request.method == 'POST':
        form = ActivityForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)

            post.state = 1
            post.user_id_id = request.user.id
            post.priority = 0
            post.want_to_join_count = 0
            post.created_at = timezone.now()
            post.save()
            messages.info(request, '活动《{}》创建成功'.format(post.name))

            print(post.id)
            if UserProfile.check_user_can_join_activity(UserProfile(),request.user.id,post.id):
                messages.info(request, '您已自动加入自己创建的活动《{}》'.format(post.name))
                Join.create_join(Join(), user_id=request.user, activity_id=post, start_time=post.start_time,
                             end_time=post.end_time, state=0)
                post.want_to_join_count = 1
                post.save()
            else:
                messages.info(request, '由于时间冲突，您未能加入自己创建的活动《{}》'.format(post.name))

            form = ActivityForm()
    else:
        form = ActivityForm()
    #params = request.POST if request.method == 'POST' else None
    #form = ActivityForm(params)


    return render(request, 'apply_activity.html', {'form': form, 'privilege': privilege})

@login_required
def join_activity(request,activity_id):
    activity = Activity.find_activity(Activity(),activity_id)
    can_join_flag = UserProfile.check_user_can_join_activity(UserProfile(),request.user.id,activity_id)
    if not can_join_flag:
        messages.info(request, '和当天已选活动冲突')
        return redirect('home')
    history_join = Join.find_join(Join(),request.user.id,activity_id,1)
    if history_join:
        messages.info(request, '你被创建者拒绝加入活动《{}》'.format(activity.name))
        return redirect('home')
    elif activity.capacity <= activity.want_to_join_count:
        messages.info(request, '活动《{}》人数已满'.format(activity.name))
        return redirect('home')
    else :
        messages.info(request, '参加活动《{}》成功'.format(activity.name))
        Msg.create_msg(Msg(),request.user,receive_user_id= activity.user_id.id,
                       title= '【系统】您好！我参加了您的活动'+ activity.name,
                       content='您好！我参加了您的活动'+activity.name+'。请多关照！')

    activity.want_to_join_count += 1
    activity.save()
    Join.create_join(Join(),request.user,activity,activity.start_time,activity.end_time,0)
    return redirect('home')


@login_required
def quit_activity(request,activity_id):
    activity = Activity.find_activity(Activity(), activity_id)
    if activity.want_to_join_count > 0:
        activity.want_to_join_count -= 1
    activity.save()
    join = Join.find_join(Join(),request.user.id,activity_id,0)
    Join.remove_join(Join(),join[0].id)
    messages.info(request, '退出活动《{}》成功'.format(activity.name))
    Msg.create_msg(Msg(), request.user, receive_user_id=activity.user_id.id,
                   title='【系统】不好意思！我退出了您的活动' + activity.name,
                   content='不好意思！我退出了您的活动' + activity.name + '。给您带来了麻烦，十分抱歉！')

    return redirect('home')

@login_required
def join_actvity_list(request,activity_id):
    activity = Activity.find_activity(Activity(),activity_id)
    joins = Join.find_all_join_users(Join(),activity_id).order_by('posted_at')
    black_joins = Join.find_all_join_users(Join(),activity_id,state = 1).order_by('posted_at')
    return render(request,'join_activity_list.html',{'joins' : joins, 'activity_id':activity_id ,'activity':activity ,'blackjoins': black_joins})

@login_required
def cancel_activity_join(request,join_id):
    join = Join.find_join_by_id(Join(),join_id)
    Join.cancel_join(Join(),join_id)
    join.activity_id.want_to_join_count -= 1
    join.activity_id.save()
    messages.info(request, '删除用户“{}”参与您的活动《{}》成功'.format(join.user_id,join.activity_id.name))

    Msg.create_msg(Msg(), request.user, receive_user_id=join.user_id.id,
                   title='【系统】不好意思！我将您删除出了我的活动' + join.activity_id.name +'的参与列表',
                   content='不好意思！我将您删除出了我的活动' + join.activity_id.name + '的参与列表。请您参与其他的活动。')
    return redirect('join_activity_list',join.activity_id.id)

@login_required
def clear_activity_join(request,join_id):
    join = Join.find_join_by_id(Join(),join_id)
    Msg.create_msg(Msg(), request.user, receive_user_id=join.user_id.id,
                   title='【系统】我将您移出了我的活动' + join.activity_id.name + '的黑名单',
                   content='我将您移出了我的活动' + join.activity_id.name + '的黑名单。您可以重新申请此活动。')

    Join.remove_join(Join(),join_id)
    messages.info(request, '将用户“{}”清除出您的活动《{}》的黑名单成功'.format(join.user_id,join.activity_id.name))
    return redirect('join_activity_list',join.activity_id.id)

@login_required
def change_activity_info(request,activity_id):
    activity = Activity.find_activity(Activity(),activity_id)
    print(activity)

    if request.method == 'POST':
        form = ActivityForm(request.POST ,instance = activity)
        if form.is_valid():
            form.save()
            messages.info(request, '活动《{}》修改成功'.format(activity.name))

    joins = Join.find_all_join_users(Join(),activity_id,state = 0)
    for join in joins:
        #给报名的用户发消息
        if request.user.id != join.user_id.id:
            Msg.create_msg(Msg(),request.user,join.user_id.id,title= '【系统】请注意！我修改了活动'+ join.activity_id.name + '的信息' ,content= '请注意！我修改了活动'+join.activity_id.name+'的信息。请提前做好准备！')
        join.delete()

    form = ActivityForm(instance=activity)
    return render(request, 'change_activity_info.html', {'form': form, 'activity': activity})


@login_required
def cancel_activity(request,activity_id):
    activity = Activity.find_activity(Activity(),activity_id)
    activity.state = 2
    activity.want_to_join_count = 0
    activity.save()

    #取消当前的报名
    joins = Join.find_all_join_users(Join(),activity_id,state = 0)
    for join in joins:
        #给报名的用户发消息
        if request.user.id != join.user_id.id:
            Msg.create_msg(Msg(),request.user,join.user_id.id,title= '【系统】抱歉！我取消了活动'+ join.activity_id.name,content = '抱歉！我取消了活动'+join.activity_id.name+'。请参加其他的活动吧！')
        join.delete()

    return redirect('show_activity',activity_id)


@login_required
def resume_activity(request,activity_id):
    Activity.update_activity_state(Activity(),activity_id,newstate = 1)
    return redirect('show_activity',activity_id)


def show_user_applied_activities(request,user_id):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            date = cd['date']
            activities = UserProfile.find_user_created_activities_in_date(UserProfile(),user_id,date)
            user = UserProfile.find_user_by_id(UserProfile(), user_id)[0]
            return render(request, 'show_user_applied_activities.html', {'activities': activities,'user':user, 'form': form})

    form = DateForm(initial={'date': timezone.now().date()})
    activities = UserProfile.find_user_created_activities_in_date(UserProfile(),user_id,timezone.now().date())
    user = UserProfile.find_user_by_id(UserProfile(),user_id)[0]
    return render(request,'show_user_applied_activities.html',{'activities':activities,'user':user,'form':form})


@login_required
def show_user_joined_activities(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            date = cd['date']
            joins = UserProfile.find_user_joined_activities(UserProfile(), request.user.id,
                                                            search_date = date)
            return render(request, 'show_user_joined_activities.html', {'joins': joins,'form':form})

    form = DateForm(initial={'date': timezone.now().date()})
    joins = UserProfile.find_user_joined_activities(UserProfile(),request.user.id,search_date = timezone.now().date())
    return render(request,'show_user_joined_activities.html',{'joins': joins,'form':form})

def show_search_activities(request):
    if request.method == 'POST':
        form = ActivitySearchForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            search_date = cd['search_date']
            name = cd['name']
            place = cd['place']
            state = cd['state']
            type = cd['type']
            print(name,place,type,state)
            activities = Activity.search_activity(Activity(), search_date, search_name=name, search_type=type, search_place=place, search_state=state)
            return render(request, 'show_search_activities.html', {'activities': activities, 'form': form})

    form = ActivitySearchForm(initial={'search_date': timezone.now().date()})
    activities = Activity.search_activity(Activity(),timezone.now().date(),search_name='',search_type='',search_place='',search_state='' )
    return render(request, 'show_search_activities.html', {'activities': activities, 'form': form})