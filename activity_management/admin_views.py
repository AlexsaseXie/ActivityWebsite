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
                arrange_activity_for_date_by_priority(date)

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
    return redirect('admin_home')


def lift_activity(request,activity_id):
    Activity.update_activity_state(Activity(),activity_id,newstate=1)
    messages.info(request,'解禁活动成功')
    return redirect('admin_home')


#贪心安排活动
def arrange_activity_for_date(date):
    candidate_activities = Activity.find_activity_in_date_state(Activity(),date)
    currentEndTime = {}
    for act in candidate_activities:
        if act.place not in currentEndTime:
            act.state = 5
            act.save()
            currentEndTime[act.place] = act.end_time
        else:
            if act.start_time > currentEndTime[act.place]:
                act.state = 5
                act.save()
                currentEndTime[act.place] = act.end_time
            else:
                act.state = 4
                act.save()
    return

#按优先级安排活动
def arrange_activity_for_date_by_priority(date):
    candidate_activities = Activity.find_activity_in_date_order_by_priority_count(Activity(),date)
    for act in candidate_activities:
        flag = Activity.check_can_add_activity(Activity(),act.id)
        if flag:
            act.state = 5
            act.save()
        else:
            act.state = 4
            act.save()
    return

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