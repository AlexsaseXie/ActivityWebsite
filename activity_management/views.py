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

# Create your views here.
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate




@static_vars(counter = 0,lastform = 0,lastactivities = 0)
def home_page(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            date = cd['date']
            activities = Activity.find_activity_in_date_available(Activity(),date)

            home_page.lastform = form
            home_page.lastactivities = activities
            return render(request, 'home.html', {'activities': activities, 'form': form})

    if home_page.counter == 0 :
        form = DateForm(initial={'date': timezone.now().date()})
        activities = Activity.find_activity_in_date_available(Activity(), timezone.now().date())
        home_page.counter += 1
        home_page.lastform = form
        home_page.lastactivities = activities
    else :
        form = home_page.lastform
        activities = home_page.lastactivities

    return render(request, 'home.html', {'activities': activities, 'form': form})


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

def multi_apply_submit(request):
    privilege = UserProfile.find_user_privilege(UserProfile(), request.user.id)
    file = request.FILES.get('file')

    # file_path = file.path
    # return HttpResponse('file:' + file_path)
    suffix = file.name.split('.')[-1]
    if not suffix == 'txt':
        return HttpResponse('Require refused: incorrect file type.')

    save_path = '../ActivityWebsite-master/uploadfiles/' + file.name[:-4] + '_'\
                + timezone.now().date().__str__() + '_'\
                + timezone.now().time().hour.__str__() + '_'\
                + timezone.now().time().minute.__str__() + '_'\
                + timezone.now().time().second.__str__()\
                + '.txt'
    path = default_storage.save(save_path, ContentFile(file.read()))
    with open(path, 'r') as f:
        line_list = f.readlines()
        if not line_list:
            return  HttpResponse('Require refused: invalid file.')
        for line in line_list:
            act_info = line.split(',')
            # name, type, description, capacity, start time, end time, place
            if not len(act_info) == 7:
                # return HttpResponse('Require refused: incorrect input form.')
                continue

            post = Activity.create_activity(Activity(), request.user, act_info[6], act_info[4], act_info[5], act_info[3], act_info[1], act_info[0], act_info[2], 0, timezone.now())
            Join.create_join(Join(), user_id=request.user, activity_id=post, start_time=post.start_time,
                             end_time=post.end_time, state=1)

        form = ActivityForm()
        messages.info(request, '已成功导入 %d 个活动' % len(line_list))
        return render(request, 'apply_activity.html', {'form': form, 'privilege': privilege})

remind_list = []

def update_ready_activities():
    ready_list = Activity.find_ready_activity_in_date_state(Activity(), timezone.now().date())

    pre_time = timezone.now()
    for act in ready_list:
        if act.start_time <= pre_time:
            Activity.update_activity_state(Activity(), act.id, 6)

            # count
            if act.state == 1:
                continue

            user_profile = UserProfile.find_user_by_id(UserProfile(), act.user_id.id)[1]
            user_profile.admitted_activity_count += 1
            user_profile.save()
            join_list = Join.find_all_join_users(Join(), act.id)
            for join in join_list:
                profile = UserProfile.find_user_by_id(UserProfile(), join.user_id.id)[1]
                profile.joined_activity_count += 1
                profile.save()

        else:
            # msg remind
            if act.state == 1:
                continue

            query = 'SELECT * FROM auth_user WHERE is_superuser = 1'
            user = User.objects.raw(query)

            if not act.user_id.id in remind_list:
                interval = act.start_time - pre_time
                if interval.seconds > 3 * 3600:
                    continue

                join_list = Join.find_all_join_users(Join(), act.id)
                for join in join_list:
                    Msg.create_msg(Msg(),
                                   user[0],
                                   join.user_id.id,
                                   '活动提醒',
                                   '你报名参加的活动 \"%s\" 还有 %d 小时 %d 分就要开始啦，记得准时参加。' \
                                   % (act.name, interval.seconds / 3600, (interval.seconds % 3600) / 60))

                remind_list.append(act.user_id.id)