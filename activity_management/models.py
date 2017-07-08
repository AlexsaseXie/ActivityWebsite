from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from django.db import connection
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True, verbose_name=('用户'))
    privilege = models.IntegerField()
    applied_activity_count = models.IntegerField()
    admitted_activity_count = models.IntegerField()
    joined_activity_count = models.IntegerField()
    real_name = models.CharField(max_length = 100,default = '')
    image = models.ImageField(upload_to="image/%Y/%m", default=u"image/default.png")

    def __str__(self):
        return '%s (%s)' % (self.user.username, self.real_name)

    #检查是否有此用户名
    def check_username_exist(self,username):
        ulist = User.objects.filter(username = username)
        if not ulist:
            return False
        else:
            return True

    # 通过用户名获得某用户的id
    def get_user_id(self, username):
        ulist = User.objects.filter(username=username)
        if not ulist:
            return -1
        else:
            return ulist[0].id

    #创建新用户
    def create_userprofile(self,uname, password, real_name, email, privilege, applied_activity_count=0,
                           admitted_activity_count=0, joined_activity_count=0):
        user = User()
        user.username = uname
        user.set_password(password)
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
        return [user,userProfile]

    # 删除用户
    def remove_userprofile(self,user_id):
        try:
            target = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return None
        target.delete()
        # targetProfile = UserProfile.objects.get(user_id = user_id)
        # targetProfile.delete()

    # 找到用户的记录
    def find_user_by_id(self,user_id):
        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
        targetProfile = UserProfile.objects.get(user_id=user_id)
        return [target, targetProfile]

    # 更新用户信息
    def update_user_info(self,user_id, new_name, new_password, new_real_name, new_email):
        try:
            target = User.objects.get(id = user_id)
        except User.DoesNotExist:
            return None
        targetProfile = UserProfile.objects.get(user_id=user_id)
        if new_name:
            target.username = new_name
        if new_password:
            target.set_password(new_password)
        if new_email:
            target.email = new_email
        if new_real_name:
            targetProfile.real_name = new_real_name
        target.save()
        targetProfile.save()
        return [target,targetProfile]

    # 找到用户的权限
    def find_user_privilege(self,user_id):
        try:
            targetProfile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return None
        return targetProfile.privilege

    # 改变用户的权限
    def change_user_privilege(self,user_id, new_privilege):
        try:
            targetProfile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return None
        targetProfile.privilege = new_privilege
        targetProfile.save()
        return targetProfile

    #判断是否参与了某个活动
    def check_user_join_activity(self,user_id,activity_id):
        result = Join.objects.filter(user_id = user_id,activity_id = activity_id,state = 0)
        if not result:
            return False
        else:
            return True

    #返回用户创建的活动列表（活动列表）
    def find_user_created_activities(self,user_id):
        activities = Activity.objects.filter(user_id=user_id)
        return activities

    # 返回某用户创建的活动列表（活动列表）
    def find_user_created_activities_in_state(self,user_id, state):
        activities = Activity.objects.filter(user_id=user_id, state=state)
        return activities

    # 返回某用户创建的某日期的活动列表
    def find_user_created_activities_in_date(self,user_id,search_date):
        query = 'SELECT *  FROM activity_management_activity WHERE user_id_id = %s  AND DATEDIFF(start_time,%s) = 0 ORDER BY start_time'
        activities = Activity.objects.raw(query, [user_id, search_date])
        return activities

    # 返回某用户参加的活动列表（参与记录）
    def find_user_joined_activities(self,user_id ,search_date,state = 0):
        query = 'SELECT *  FROM activity_management_join WHERE user_id_id = %s AND state = %s AND DATEDIFF(start_time,%s) = 0 ORDER BY start_time'
        join = Join.objects.raw(query,[ user_id ,state ,search_date ])
        return join

    # 返回某用户的所有消息
    def find_user_msgs(self,user_id, state):
        msgs = Msg.objects.filter(receive_user_id=user_id, state=state).order_by('created_at')
        return msgs

    #返回某用户未读消息个数
    def count_user_unread_msgs(self,user_id,state = 0):
        msgs = Msg.objects.filter(receive_user_id=user_id, state=state)
        count = 0
        for m in msgs:
            count += 1
        return count

    #检查用户是否可以参加某个活动
    def check_user_can_join_activity(self,user_id,activity_id):
        activity = Activity.find_activity(Activity(),activity_id)
        query = 'SELECT *  FROM activity_management_join WHERE user_id_id = %s AND state = 0 AND (NOT((start_time <= %s AND end_time <= %s) OR (start_time >= %s AND end_time >= %s)))'
        joins = Join.objects.raw(query,[user_id, activity.start_time , activity.start_time,activity.end_time,activity.end_time])
        count = 0
        for join in joins:
            count +=1
        if count == 0:
            return True
        else:
            return False

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

    def __str__(self):
        return '%s (%s)' % (self.name, self.created_at)

    # 创建活动
    def create_activity(self,user_id, place, start_time, end_time, capacity, type, name, description, priority, created_at,
                        want_to_join_count=0, state=1):
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
        return activity

    # 删除活动
    def remove_activity(self,activity_id):
        try:
            target = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return None
        target.delete()

    # 找到活动的信息
    def find_activity(self,activity_id):
        try:
            target = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return None
        return target

    # 更新活动信息
    def update_activity(self,activity_id, user_id, place, start_time, end_time, capacity, type, name, description, priority,
                        created_at, want_to_join_count, state):
        try:
            activity = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return None
        if user_id:
            activity.user_id = user_id
        if place:
            activity.place = place
        if start_time:
            activity.start_time = start_time
        if end_time:
            activity.end_time = end_time
        if state:
            activity.state = state
        if capacity:
            activity.capacity = capacity
        if type:
            activity.type = type
        if name:
            activity.name = name
        if description:
            activity.description = description
        if priority:
            activity.priority = priority
        if want_to_join_count:
            activity.want_to_join_count = want_to_join_count
        if created_at:
            activity.created_at = created_at
        activity.save()
        return activity

    #更改活动的状态
    def update_activity_state(self,activity_id,newstate):
        try:
            activity = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return None
        activity.state = newstate
        activity.save()
        return activity

    #返回活动的时长
    def activity_length(self,activity_id):
        query = 'SELECT TIMESTAMPDIFF(MINUTE,start_time,end_time) AS time_length FROM activity_management_activity WHERE activity_id = %d LIMIT 1'
        activities = Activity.objects.raw(query,[activity_id])
        return activities[0].time_length

    #返回日期的所有活动
    def find_activity_in_date(self,search_date):
        query = 'SELECT *,TIMESTAMPDIFF(MINUTE,start_time,end_time) AS time_length FROM activity_management_activity WHERE TO_DAYS(start_time) = TO_DAYS(%s) ORDER BY ' \
                'start_time,end_time'
        activities = Activity.objects.raw(query,[search_date])
        return activities

    # 搜索活动
    def search_activity(self, search_date, search_name, search_type, search_place, search_state):
        if search_date:
            query = 'SELECT * FROM activity_management_activity WHERE TO_DAYS(start_time) = TO_DAYS(%s) '
            all_activities = Activity.objects.raw(query, [search_date])
        else:
            all_activities = Activity.objects.all()
        result_activities = []
        for act in all_activities:
            flag = True
            if search_name:
                #if act.name != search_name:
                if act.name.lower().find(search_name.lower()) == -1:
                    flag = False
            if search_type:
                if act.type != search_type:
                    flag = False
            if search_place:
                # if act.place != search_place:
                if act.place.lower().find(search_place.lower()) == -1:
                    flag = False
            if search_state:
                if act.state != search_state:
                    flag = False
            if flag:
                result_activities.append(act)

        return result_activities


    #返回日期的所有可以报名的活动
    def find_activity_in_date_available(self,search_date):
        query = 'SELECT *,TIMESTAMPDIFF(MINUTE,start_time,end_time) AS time_length FROM activity_management_activity WHERE TO_DAYS(start_time) = TO_DAYS(%s) ' \
                'AND (state = 1 OR state = 5) ORDER BY start_time,end_time'
        activities = Activity.objects.raw(query, [search_date])
        return activities

    #返回日期内所有申请中的活动，根据结束时间，想要加入的人数排序
    def find_activity_in_date_state(self,search_date):
        query = 'SELECT *,TIMESTAMPDIFF(MINUTE,start_time,end_time) AS time_length FROM activity_management_activity WHERE TO_DAYS(start_time) = TO_DAYS(%s) ' \
                'AND state = 1 ORDER BY end_time,-want_to_join_count,start_time'
        activities = Activity.objects.raw(query, [search_date])
        return activities

    # 搜索日期内申请中和等待举办的活动
    def find_ready_activity_in_date_state(self, search_date):
        query = 'SELECT *,TIMESTAMPDIFF(MINUTE,start_time,end_time) AS time_length FROM activity_management_activity WHERE TO_DAYS(start_time) = TO_DAYS(%s) ' \
                'AND state = 1 or state = 5 ORDER BY end_time,start_time'
        activities = Activity.objects.raw(query, [search_date])
        return activities


    #返回日期内所有申请中的活动，按照优先级，想要加入的人数排序
    def find_activity_in_date_order_by_priority_count(self,search_date):
        query = 'SELECT *,TIMESTAMPDIFF(MINUTE,start_time,end_time) AS time_length FROM activity_management_activity WHERE TO_DAYS(start_time) = TO_DAYS(%s) ' \
                'AND state = 1 ORDER BY -priority,-want_to_join_count'
        activities = Activity.objects.raw(query, [search_date])
        return activities

    #检查当天是否可以加入这个活动
    def check_can_add_activity(self,activity_id):
        activity = Activity.find_activity(Activity(),activity_id = activity_id)
        query = 'SELECT *  FROM activity_management_activity WHERE state = 5 AND place =  %s AND (NOT((start_time <= %s AND end_time <= %s) OR (start_time >= %s AND end_time >= %s)))'
        acts = Activity.objects.raw(query,[activity.place ,activity.start_time , activity.start_time,activity.end_time,activity.end_time])
        count = 0
        for act in acts:
            count +=1
            if count > 0:
                break

        if count == 0:
            return True
        else:
            return False


    #返回所在日期，该类型的所有活动
    def find_activity_in_date_type(self,search_date,search_type):
        if search_type!= None:
            query = 'SELECT *,TIMESTAMPDIFF(MINUTE,start_time,end_time) AS time_length FROM activity_management_activity WHERE TO_DAYS(start_time) = TO_DAYS(%s) and type = %s'
            activities = Activity.objects.raw(query,[search_date,search_type])
            return activities
        else :
            query = 'SELECT *,TIMESTAMPDIFF(MINUTE,start_time,end_time) AS time_length FROM activity_management_activity WHERE TO_DAYS(start_time) = TO_DAYS(%s)'
            activities = Activity.objects.raw(query, [search_date])
            return activities


class Join(models.Model):
    id = models.AutoField(primary_key = True)
    user_id = models.ForeignKey(User)
    activity_id = models.ForeignKey(Activity)
    start_time = models.DateTimeField(blank = True)
    end_time = models.DateTimeField(blank = True)
    state = models.IntegerField()
    posted_at = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return '%s %s (%s)' % (self.user_id, self.activity_id ,self.posted_at)

    # 创建参与记录
    def create_join(self,user_id, activity_id, start_time, end_time, state=0):
        join = Join()
        join.user_id = user_id
        join.activity_id = activity_id
        join.start_time = start_time
        join.end_time = end_time
        join.state = state
        join.save()
        return join

    # 更改参与信息
    def update_join(self,join_id, start_time, end_time):
        try:
            join = Join.objects.get(id=join_id)
        except Join.DoesNotExist:
            return None
        join.start_time = start_time
        join.end_time = end_time
        join.save()
        return join

    # 取消参与
    def cancel_join(self,join_id):
        try:
            join = Join.objects.get(id=join_id)
        except Join.DoesNotExist:
            return None
        join.state = 1
        join.save()
        return join

    # 删除参与
    def remove_join(self,join_id):
        try:
            join = Join.objects.get(id=join_id)
        except Join.DoesNotExist:
            return None
        join.delete()

    # 找到参与记录
    def find_join(self,user_id,activity_id,state = 0):
        join = Join.objects.filter(user_id = user_id,activity_id = activity_id,state = state)
        return join
    #找到此条参与记录
    def find_join_by_id(self,join_id):
        try:
            join = Join.objects.get(id=join_id)
        except Join.DoesNotExist:
            return None
        return join

    #找到该活动的所有参加者
    def find_all_join_users(self,activity_id,state = 0):
        joins = Join.objects.filter(activity_id = activity_id,state = state)
        return joins

class Msg(models.Model):
    id = models.AutoField(primary_key = True)
    from_user_id = models.ForeignKey(User)
    receive_user_id = models.IntegerField(default = 0)
    title = models.CharField(max_length = 100)
    content = models.TextField()
    posted_at = models.DateTimeField(default = timezone.now)
    state = models.IntegerField(default = 0)

    #创建消息
    def create_msg(self,from_user_id,receive_user_id,title,content):
        msg = Msg()
        msg.content = content
        msg.title = title
        msg.from_user_id = from_user_id
        msg.receive_user_id = receive_user_id
        msg.save()
        return msg

    # 删除消息
    def remove_msg(self,msg_id):
        try:
            target = Msg.objects.get(id=msg_id)
        except Msg.DoesNotExist:
            return None
        target.delete()

    # 设置消息为已读
    def set_msg_read(self,msg_id):
        try:
            target = Msg.objects.get(id=msg_id)
        except Msg.DoesNotExist:
            return None
        target.state = 1
        target.save()
        return target

    # 找到某用户的相关消息
    def find_all_msgs(self,user_id):
        msgs = Msg.objects.filter(receive_user_id=user_id).order_by('state','-posted_at')
        return msgs

    # 通过id找到某信息
    def find_msg(self,msg_id):
        try:
            target = Msg.objects.get(id=msg_id)
        except Msg.DoesNotExist:
            return None
        return target