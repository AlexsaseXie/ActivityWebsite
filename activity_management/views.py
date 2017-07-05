from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from .models import UserProfile, Activity, Join, Msg
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .forms import ActivityForm,DateForm,MessageForm,ActivitySearchForm

import xlrd

# Create your views here.

def home_page(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            date = cd['date']
            activities = Activity.find_activity_in_date_available(Activity(),date)
            return render(request, 'home.html', {'activities': activities, 'form': form})

    form = DateForm(initial={'date': timezone.now().date()})
    activities = Activity.find_activity_in_date_available(Activity(), timezone.now().date())
    return render(request, 'home.html', {'activities': activities, 'form': form})


#活动相关
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
        post.state = 1
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


@login_required
def cancel_activity(request,activity_id):
    Activity.update_activity_state(Activity(),activity_id,newstate = 2)
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
    '''
    if form.is_valid():
        post = form.save(commit=False)
        post.from_user_id = request.user.id
        post.receive_user_id = UserProfile.get_user_id(UserProfile(), request.POST.get('receive_user_name'))
        post.save()
        if (post.receive_user_id != -1):
            messages.info(request, '消息已成功发送给用户“{}”'.format(request.POST.get('receive_user_name')))
        else:
            messages.info(request, '用户“{}”不存在'.format(request.POST.get('receive_user_name')))
        form = MessageForm()
        msg = Msg.create_msg(post.from_user_id,post.receive_user_id,request.POST.get('title'),request.POST.get('content'))
    '''
    return render(request, 'send_message.html', {'form': form})

@login_required
def unread_message(request):
    msgs = Msg.find_all_msgs(Msg(), request.user.id).order_by('posted_at')
    return render(request, 'unread_message.html',{'msgs' : msgs})


def multi_apply_submit(request):
    privilege = UserProfile.find_user_privilege(UserProfile(), request.user.id)
    file = request.FILES.get('file')

    suffix = file.name.split('.')[-1]
    if not (suffix == 'txt' or 'xls'):
        return HttpResponse('Require refused: incorrect file type.')

    save_path = '../ActivityWebsite/uploadfiles/' + file.name[:-4] + '_' \
                + timezone.now().date().__str__() + '_' \
                + timezone.now().time().hour.__str__() + '_' \
                + timezone.now().time().minute.__str__() + '_' \
                + timezone.now().time().second.__str__() \
                + '.' + suffix

    path = default_storage.save(save_path, ContentFile(file.read()))

    act_num = load_activities_from_file(request.user, path)


    # ---
    '''''
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

            Activity.create_activity(Activity(), request.user, act_info[6], act_info[4], act_info[5], act_info[3], act_info[1], act_info[0], act_info[2], 0, timezone.now())
    
    '''
    form = ActivityForm()
    if act_num == 0:
        messages.warning(request, '没有导入活动')
    else:
        messages.info(request, '已成功导入 %d 个活动' % act_num)
    return render(request, 'apply_activity.html', {'form': form, 'privilege': privilege})


def load_activities_from_file(user, file_path):
    suffix = file_path.split('.')[-1]
    valid_number = 0

    if suffix == 'txt':
        with open(file_path, 'r') as f:
            line_list = f.readlines()
            if not line_list:
                return 0

            for line in line_list:
                act_info = line.split('#')
                if not len(act_info) == 7:
                    continue

                Activity.create_activity(Activity(), user, act_info[0], act_info[1], act_info[2], act_info[3],
                                         act_info[4], act_info[5], act_info[6], 0, timezone.now())
                valid_number += 1

            return valid_number

    elif suffix == 'xls':
        with xlrd.open_workbook(file_path) as f:
            sheet = f.sheet_by_index(0)
            if not sheet:
                return 0
            nrow = sheet.nrows
            ncol = sheet.ncols
            row_list = []
            for i in range(nrow):
                row_list.append(sheet.row_values(i))

            for act_info in row_list:
                if not len(act_info) == 7:
                    continue

                Activity.create_activity(Activity(), user, act_info[0], act_info[1], act_info[2], act_info[3],
                                         act_info[4], act_info[5], act_info[6], 0, timezone.now())
                valid_number += 1

            return valid_number

    else:
        return 0