from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from .models import UserProfile, Activity, Join, Msg
from django.utils import timezone
from django.contrib import messages

from .forms import ActivityForm,UploadImageForm


def show_user_info(request,user_id):
    if request.method == 'POST':
        form = UploadImageForm(request.POST)

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
