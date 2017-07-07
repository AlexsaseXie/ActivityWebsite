from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from .models import UserProfile, Activity, Join, Msg
from django.utils import timezone
from django.contrib import messages

from .forms import DateForm

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


@static_vars(counter = 0,lastform = 0,lastactivities = 0)
def admin_home(request):
    #time_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            if 'search' in request.POST:
                cd = form.cleaned_data
                date = cd['date']
                activities = Activity.find_activity_in_date(Activity(),date)

                admin_home.lastform = form
                admin_home.lastactivities = activities
                return render(request, 'admin_home.html', {'activities': activities, 'form': form})
            else :
                cd = form.cleaned_data
                date = cd['date']
                activities = Activity.find_activity_in_date(Activity(), date)

                arrange_activity_for_date_by_priority(request.user,date)

                admin_home.lastform = form
                admin_home.lastactivities = activities
                return render(request, 'admin_home.html', {'activities': activities, 'form': form})

    if (admin_home.counter == 0):
        form = DateForm(initial={'date': timezone.now().date()})
        activities = Activity.find_activity_in_date(Activity(),timezone.now().date())
        admin_home.lastform = form
        admin_home.lastactivities = activities
        admin_home.counter += 1
    else :
        form = admin_home.lastform
        activities = admin_home.lastactivities

    return render(request, 'admin_home.html',{'activities' : activities , 'form' : form})


def ban_activity(request,activity_id):
    Activity.update_activity_state(Activity(),activity_id,newstate=3)
    messages.info(request,'禁用活动成功')
    activity = Activity.find_activity(Activity(), activity_id)
    Msg.create_msg(Msg(), request.user, activity.user_id.id, title='【系统】您的活动' + activity.name + '涉嫌违规，已被管理员禁用',
                   content='您的活动' + activity.name + '涉嫌违规，已被管理员禁用。')

    send_messages_for_creator_participates(request.user,activity_id,state= 3 )

    # 取消当前的报名
    joins = Join.find_all_join_users(Join(), activity.id, state=0)
    for join in joins:
        join.delete()
    activity.want_to_join_count = 0
    activity.save()
    return redirect('admin_home')


def lift_activity(request,activity_id):
    Activity.update_activity_state(Activity(),activity_id,newstate=1)
    messages.info(request,'解禁活动成功')
    activity = Activity.find_activity(Activity(),activity_id)
    Msg.create_msg(Msg(), request.user, activity.user_id.id, title='【系统】管理员解除了对您的活动' + activity.name + '的禁用',
                   content='管理员解除了对您的活动' + activity.name + '的禁用')

    return redirect('admin_home')


#贪心安排活动
def arrange_activity_for_date(user,date):
    candidate_activities = Activity.find_activity_in_date_state(Activity(),date)
    currentEndTime = {}
    for act in candidate_activities:
        if act.place not in currentEndTime:
            act.state = 5
            act.save()
            send_messages_for_creator_participates(user, act.id, state=5)
            currentEndTime[act.place] = act.end_time
        else:
            if act.start_time > currentEndTime[act.place]:
                act.state = 5
                act.save()
                send_messages_for_creator_participates(user, act.id, state=5)
                currentEndTime[act.place] = act.end_time
            else:
                act.state = 4
                send_messages_for_creator_participates(user, act.id, state=4)
                # 取消当前的报名
                joins = Join.find_all_join_users(Join(), act.id, state=0)
                for join in joins:
                    join.delete()
                act.want_to_join_count = 0
                act.save()
    return

#按优先级安排活动
def arrange_activity_for_date_by_priority(user,date):
    candidate_activities = Activity.find_activity_in_date_order_by_priority_count(Activity(),date)
    for act in candidate_activities:
        flag = Activity.check_can_add_activity(Activity(),act.id)
        if flag:
            act.state = 5
            act.save()
            send_messages_for_creator_participates(user,act.id,state = 5)
        else:
            act.state = 4
            send_messages_for_creator_participates(user, act.id, state=4)
            # 取消当前的报名
            joins = Join.find_all_join_users(Join(), act.id, state=0)
            for join in joins:
                join.delete()
            act.want_to_join_count = 0
            act.save()
    return

#给相关者发送信息
def send_messages_for_creator_participates(user,activity_id,state):
    joins = Join.find_all_join_users(Join(),activity_id)
    for join in joins:
        if state == 4 or state == 3:
            if join.user_id != join.activity_id.user_id :
                Msg.create_msg(Msg(), user, join.user_id.id, title='【系统】管理员取消了您参与的活动' + join.activity_id.name ,
                       content='管理员取消了您参与的活动' + join.activity_id.name + '。具体情况请查看该活动的活动信息。')
            else :
                Msg.create_msg(Msg(), user, join.user_id.id, title='【系统】管理员取消了您创建的活动' + join.activity_id.name,
                           content='管理员取消了您创建的活动' + join.activity_id.name + '。具体情况请查看该活动的活动信息。')
        elif state == 5:
            if join.user_id != join.activity_id.user_id :
                Msg.create_msg(Msg(), user, join.user_id.id, title='【系统】管理员选中了您参与的活动' + join.activity_id.name ,
                       content='管理员选中了您参与的活动' + join.activity_id.name + '。请耐心等待活动的举办。')
            else :
                Msg.create_msg(Msg(), user, join.activity_id.user_id.id, title='【系统】管理员选中了您创建的活动' + join.activity_id.name,
                           content='管理员选中了您创建的活动' + join.activity_id.name + '。请耐心等待活动的举办。')


def admin_raise_priority(request,activity_id):
    act = Activity.find_activity(Activity(),activity_id)
    act.priority += 1
    act.save()
    return redirect('admin_show_activity',activity_id)

# m._b S
def degrade_user(request, user_id):
    if UserProfile.find_user_privilege(UserProfile(), user_id) == 1:
        UserProfile.change_user_privilege(UserProfile(), user_id, 0)

    return admin_user_info(request, user_id)


def upgrade_user(request, user_id):
    if UserProfile.find_user_privilege(UserProfile(), user_id) == 0:
        UserProfile.change_user_privilege(UserProfile(), user_id, 1)

    return admin_user_info(request, user_id)


def admin_show_activity(request,activity_id):
    act = Activity.find_activity(Activity(), activity_id)
    return render(request, 'admin_show_activity.html', {'activity': act})

def admin_user_info(request, user_id):
    user = UserProfile.find_user_by_id(UserProfile(), user_id)
    if UserProfile.find_user_privilege(UserProfile(), request.user.id) == 2:
        return render(request, 'admin_user_info.html', {'user_obj': user[0], 'user_profile': user[1]})
    else:
        return HttpResponse('Require refused: authentication failed.')


@login_required
def enter_admin(request):
    if UserProfile.find_user_privilege(UserProfile(), request.user.id) == 2:
        return redirect('admin_home')
    else:
        return HttpResponse('Require refused: authentication failed.')