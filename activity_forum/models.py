from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True, verbose_name=('用户'))
    privilege = models.IntegerField()
    applied_activity_count = models.IntegerField()
    admitted_activity_count = models.IntegerField()
    joined_activity_count = models.IntegerField()
    real_name = models.CharField(max_length = 100,default = '')

    # 创建新用户
    def create_userprofile(uname, password, real_name, email, privilege, applied_activity_count=0,
                           admitted_activity_count=0, joined_activity_count=0):
        user = User()
        user.username = uname
        user.set_password = password
        user.email = email
        user.save()
        userProfile = UserProfile()
        userProfile.user_id = user.id
        userProfile.privilege = privilege
        userProfile.applied_activity_count = applied_activity_count
        userProfile.admitted_activity_count = admitted_activity_count
        userProfile.joined_activity_count = joined_activity_count
        userProfile.real_name = real_name
        userProfile.save()

    # 删除用户
    def remove_userprofile(user_id):
        try:
            target = User.objects.get(user_id=user_id)
        except DoNotExist:
            return None
        target.delete()
        # targetProfile = UserProfile.objects.get(user_id = user_id)
        # targetProfile.delete()

    # 找到用户的记录
    def find_user_by_id(user_id):
        try:
            target = User.objects.get(user_id=user_id)
        except DoNotExist:
            return None
        targetProfile = UserProfile.objects.get(user_id=user_id)
        return [target, targetProfile]

    # 更新用户信息
    def update_user_info(user_id, new_name, new_password, new_real_name, new_email):
        try:
            target = User.objects.get(user_id=user_id)
        except DoNotExist:
            return None
        targetProfile = UserProfile.objects.get(user_id=user_id)
        if new_name!=None:
            target.username = new_name
        if new_password!=None:
            target.password = new_password
        if new_email!=None:
            target.email = new_email
        if new_real_name!=None:
            targetProfile.real_name = new_real_name
        target.save()
        targetProfile.save()

    # 改变用户的权限
    def change_user_privilege(user_id, new_privilege):
        try:
            targetProfile = UserProfile.objects.get(user_id=user_id)
        except DoNotExist:
            return None
        targetProfile.privilege = new_privilege

    # 返回某用户创建的活动列表
    def find_user_created_activities(user_id, state):
        activities = Activity.objects.filter(user_id=user_id, state=state)
        return activities

    # 返回某用户参加的活动列表（参与记录）
    def find_user_joined_activities(user_id, state=0):
        activities = Join.objects.filter(user_id=user_id, state=state)
        return activities

    # 返回某用户的所有消息
    def find_user_msgs(user_id, state):
        msgs = Msg.objects.filter(receive_user_id=user_id, state=state)
        return msgs

class Activity(models.Model):
    id = models.AutoField(primary_key = True)
    user_id = models.ForeignKey(User)
    place = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    state = models.IntegerField()
    capacity = models.IntegerField()
    want_to_join_count = models.IntegerField()
    type = models.CharField(max_length = 50)
    name = models.CharField(max_length = 100)
    description = models.TextField()
    priority = models.IntegerField()
    created_at = models.DateTimeField(default = timezone.now)

    # 创建活动
    def create_activity(user_id, place, start_time, end_time, capacity, type, name, description, priority, created_at,
                        want_to_join_count=0, state=0):
        activity = Activity()
        activity.user_id = user_id
        activity.place = place
        activity.start_time = start_time
        activity.end_time = end_time
        activity.state = state
        activity.capacity = capacity
        activity.type = type
        activity.name = name
        activity.description = description
        activity.priority = priority
        activity.want_to_join_count = want_to_join_count
        activity.created_at = created_at
        activity.save()

    # 删除活动
    def remove_activity(activity_id):
        try:
            target = Activity.objects.get(id=activity_id)
        except DoNotExist:
            return None
        target.delete()

    # 找到活动的信息
    def find_activity(activity_id):
        try:
            target = Activity.objects.get(id=activity_id)
        except DoNotExist:
            return None
        return target

    # 更新活动信息
    def update_activity(activity_id, user_id, place, start_time, end_time, capacity, type, name, description, priority,
                        created_at, want_to_join_count, state):
        try:
            activity = Activity.objects.get(id=activity_id)
        except DoNotExist:
            return None
        if user_id!=None:
            activity.user_id = user_id
        if place!=None:
            activity.place = place
        if start_time!=None:
            activity.start_time = start_time
        if end_time!=None:
            activity.end_time = end_time
        if state!=None:
            activity.state = state
        if capacity!=None:
            activity.capacity = capacity
        if type!=None:
            activity.type = type
        if name!=None:
            activity.name = name
        if description!=None:
            activity.description = description
        if priority!=None:
            activity.priority = priority
        if want_to_join_count!=None:
            activity.want_to_join_count = want_to_join_count
        if created_at!=None:
            activity.created_at = created_at
        activity.save()

class Join(models.Model):
    id = models.AutoField(primary_key = True)
    user_id = models.ForeignKey(User)
    activity_id = models.ForeignKey(Activity)
    start_time = models.DateTimeField(blank = True)
    end_time = models.DateTimeField(blank = True)
    state = models.IntegerField()
    posted_at = models.DateTimeField(default = timezone.now)

    # 创建参与记录
    def create_join(user_id, activity_id, start_time, end_time, state=0):
        join = Join()
        join.user_id = user_id
        join.activity_id = activity_id
        join.start_time = start_time
        join.end_time = end_time
        join.state = state
        join.save()

    # 更改参与信息
    def update_join(join_id, start_time, end_time):
        try:
            join = Join.objects.get(id=join_id)
        except DoNotExist:
            return None
        join.start_time = start_time
        join.end_time = end_time
        join.save()

    # 取消参与
    def cancel_join(join_id):
        try:
            join = Join.objects.get(id=join_id)
        except DoNotExist:
            return None
        join.state = 1
        join.save()

    # 删除参与
    def remove_join(join_id):
        try:
            join = Join.objects.get(id=join_id)
        except DoNotExist:
            return None
        join.delete()

class Msg(models.Model):
    id = models.AutoField(primary_key = True)
    from_user_id = models.ForeignKey(User)
    receive_user_id = models.IntegerField(default = 0)
    title = models.CharField(max_length = 100)
    content = models.TextField()
    posted_at = models.DateTimeField(default = timezone.now)
    state = models.IntegerField(default = 0)

    #创建消息
    def create_msg(from_user_id,receive_user_id,title,content):
        msg = Msg()
        msg.content = content
        msg.title = title
        msg.from_user_id = from_user_id
        msg.receive_user_id = receive_user_id
        msg.save()

    # 删除消息
    def remove_msg(msg_id):
        try:
            target = Msg.objects.get(id=msg_id)
        except DoNotExist:
            return None
        target.delete()

    # 设置消息为已读
    def set_msg_read(msg_id):
        try:
            target = Msg.objects.get(id=msg_id)
        except DoNotExist:
            return None
        target.state = 1
        target.save()




































