from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from .models import UserProfile, Activity, Join, Msg
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST

from .forms import ActivityForm

# Create your views here.

def home_page(request):
    time_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    activities = Activity.find_activity_in_date(Activity(),time_str)
    return render(request, 'home.html',{'activities' : activities})

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

def show_activity(request,activity_id):
    act = Activity.find_activity(Activity(),activity_id)
    return render(request, 'show_activity.html' ,{'activity':act,'joined': UserProfile.check_user_join_activity(UserProfile(),request.user.id,activity_id)})

@login_required
def apply_activity(request):
    privilege = UserProfile.find_user_privilege(UserProfile(),request.user.id)

    params = request.POST if request.method == 'POST' else None
    form = ActivityForm(params)
    if form.is_valid():
        post = form.save(commit=False)
        post.user_id_id = request.user.id
        post.priority = 0
        post.want_to_join_count = 0
        post.created_at = timezone.now()
        post.save()
        messages.info(request, '活动《{}》创建成功'.format(post.name))
        form = ActivityForm()

    return render(request, 'apply_activity.html', {'form': form, 'privilege': privilege})

@login_required
def join_activity(request,activity_id):
    activity = Activity.find_activity(Activity(),activity_id)
    history_join = Join.find_join(Join(),request.user.id,activity_id,1)
    if history_join:
        messages.info(request, '你被创建者拒绝加入活动《{}》'.format(activity.name))
        return redirect('home')
    elif activity.capacity <= activity.want_to_join_count:
        messages.info(request, '活动《{}》人数已满'.format(activity.name))
        return redirect('home')
    else :
        messages.info(request, '参加活动《{}》成功'.format(activity.name))

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
    return redirect('join_activity_list',join.activity_id.id)

@login_required
def clear_activity_join(request,join_id):
    join = Join.find_join_by_id(Join(),join_id)
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

    form = ActivityForm(instance=activity)
    return render(request, 'change_activity_info.html', {'form': form, 'activity': activity})


