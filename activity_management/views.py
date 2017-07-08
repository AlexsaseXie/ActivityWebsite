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
import xlrd
from .email import send_emails

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




def multi_apply_submit(request):
    privilege = UserProfile.find_user_privilege(UserProfile(), request.user.id)
    file = request.FILES.get('file')
    suffix = file.name.split('.')[-1]
    if not (suffix == 'txt' or 'xls'):
        return HttpResponse('Require refused: incorrect file type.')
    save_path = '../media/uploadfiles/' + file.name[:-4] + '_' \
                + timezone.now().date().__str__() + '_' \
                + timezone.now().time().hour.__str__() + '_' \
                + timezone.now().time().minute.__str__() + '_' \
                + timezone.now().time().second.__str__() \
                + '.' + suffix
    path = default_storage.save(save_path, ContentFile(file.read()))
    new_path = save_path[1:]
    print(path)
    act_num = load_activities_from_file(request.user, new_path)
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
                act = Activity.create_activity(Activity(), user, act_info[0], act_info[1], act_info[2], act_info[3],
                                         act_info[4], act_info[5], act_info[6], 0, timezone.now())
                if UserProfile.check_user_can_join_activity(UserProfile(),user.id,act.id):
                    act.want_to_join_count = 1
                    act.save()
                    Join.create_join(Join(), user_id=user, activity_id=act, start_time=act.start_time,
                                     end_time=act.end_time, state=0)
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
                act = Activity.create_activity(Activity(), user, act_info[0], act_info[1], act_info[2], act_info[3],
                                         act_info[4], act_info[5], act_info[6], 0, timezone.now())
                if UserProfile.check_user_can_join_activity(UserProfile(),user.id,act.id):
                    act.want_to_join_count = 1
                    act.save()
                    Join.create_join(Join(), user_id=user, activity_id=act, start_time=act.start_time,
                                     end_time=act.end_time, state=0)
                valid_number += 1
            return valid_number
    else:
        return 0

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

def email_remind():
    ready_list = Activity.find_ready_activity_in_date_state(Activity(), timezone.now().date())
    pre_time = timezone.now()

    user_join_list = {}

    for act in ready_list:
        if act.state == 5 and act.start_time > pre_time:
            join_list = Join.find_all_join_users(Join(), act.id)
            for join in join_list:
                if not join.user_id.id in user_join_list:
                    user_join_list[join.user_id.id] = []
                user_join_list[join.user_id.id].append(act.id)

    for user_id in user_join_list:
        act_id_list = user_join_list[user_id]
        if not act_id_list:
            continue
        date = pre_time.date()
        user = UserProfile.find_user_by_id(UserProfile(), user_id)
        email_title = '【活动管理网站】 ' + date.__str__() + '活动提醒'
        email_address = user[0].email
        email_content = '尊敬的 %s ：\n' % user[0].username
        email_content += '您在今日共有 %d 个活动，活动信息如下。\n' % len(act_id_list)

        hour_fix = 8

        for act_id in act_id_list:
            act = Activity.find_activity(Activity(), act_id)
            email_content += '————————————————————\n'
            email_content += '%s \n' % act.name
            email_content += '发布者：%s \n' % act.user_id.username
            minute_str = str(act.start_time.minute) if act.start_time.minute >= 10 else ('0' + str(act.start_time.minute))
            email_content += '开始时间：%d : ' % ((act.start_time.hour + hour_fix) % 24)
            email_content += minute_str
            email_content += '\n'

        email_content += '\n请注意准时参加。'

        ans = send_emails([email_address], email_title, email_content)
        print('send to ' + email_address + str(ans))


@login_required
def upload_image(request):
    image = request.FILES.get('images')
    suffix = image.name.split('.')[-1]
    if image.size > 10000 and image.size < 20480000 and (suffix == 'jpg'or 'png' or 'gif'):
        path = default_storage.save('../media/image/'+request.user.username+'/ '+image.name,ContentFile(image.read()))
        user_profile = UserProfile.find_user_by_id(UserProfile(),request.user.id)[1]
        user_profile.image = 'image/'+ request.user.username+'/ '+image.name
        user_profile.save()
        print(True)
        messages.info(request, "修改头像成功！")
        return redirect('show_user_info',request.user.id)
    else:
        messages.info(request,"头像的格式有问题！")
        return redirect('show_user_info', request.user.id)

    return redirect('show_user_info',request.user.id)