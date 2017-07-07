from django.conf.urls import url
from . import views
from . import auth_views
from . import user_views
from . import admin_views
from . import activity_views
from . import msg_views
from apscheduler.scheduler import Scheduler
from activity_management.views import update_ready_activities,email_remind


sched = Scheduler()


@sched.interval_schedule(seconds=300)
def tasks():
    update_ready_activities()

@sched.cron_schedule(hour=22, minute=12)
def email_examine():
    email_remind()

sched.start()



urlpatterns = [
    # home page
    url(r'^$', views.home_page, name='home'),

    # sign up
    url(r'^sign_up$', auth_views.sign_up, name='sign_up'),
    url(r'^sign_up/submit$', auth_views.sign_up_submit, name='sign_up_submit'),

    # log
    url(r'^log_in$', auth_views.log_in, name='log_in'),
    url(r'^log_in/submit$', auth_views.log_in_submit, name='log_in_submit'),
    url(r'^log_out$', auth_views.log_out, name='log_out'),

    # auth
    url(r'^authenticate$', auth_views.authenticate, name='authenticate'),
    url(r'^authenticate/submit$', auth_views.authenticate_submit, name='authenticate_submit'),

    # info
    url(r'change_info$', user_views.change_info, name='change_info'),
    url(r'change_info/submit$', user_views.change_info_submit, name='change_info_submit'),
    url(r'show_user_info/([1-9][0-9]*)$', user_views.show_user_info, name='show_user_info'),


    #activity
    url(r'apply_activity$',activity_views.apply_activity,name = 'apply_activity'),
    url(r'show_activity/([1-9][0-9]*)$',activity_views.show_activity,name = 'show_activity'),
    url(r'join_activity/([1-9][0-9]*)$', activity_views.join_activity,name='join_activity'),
    url(r'quit_activity/([1-9][0-9]*)$',activity_views.quit_activity,name = 'quit_activity'),
    url(r'join_activity_list/([1-9][0-9]*)$',activity_views.join_actvity_list,name = 'join_activity_list'),
    url(r'cancel_activity_join/([1-9][0-9]*)$',activity_views.cancel_activity_join,name = 'cancel_activity_join'),
    url(r'clear_activity_join/([1-9][0-9]*)$',activity_views.clear_activity_join,name = 'clear_activity_join'),
    url(r'change_activity_info/([1-9][0-9]*)$',activity_views.change_activity_info,name = 'change_activity_info'),
    url(r'cancel_activity/([1-9][0-9]*)$',activity_views.cancel_activity,name = 'cancel_activity'),
    url(r'resume_activity/([1-9][0-9]*)$',activity_views.resume_activity,name = 'resume_activity'),
    #url(r'user_info$', user_views.user_info, name='user_info'),
    url(r'^multi_apply_submit$', views.multi_apply_submit, name='multi_apply_submit'),
    url(r'show_search_activities$', activity_views.show_search_activities, name='show_search_activities'),

    url(r'show_user_applied_activities/([1-9][0-9]*)$',activity_views.show_user_applied_activities,name = 'show_user_applied_activities'),
    url(r'show_user_joined_activities$',activity_views.show_user_joined_activities,name = 'show_user_joined_activities'),

    #admin
    url(r'admin_home$', admin_views.admin_home, name='admin_home'),
    url(r'ban_activity/([1-9][0-9]*)$',admin_views.ban_activity,name = 'ban_activity'),
    url(r'lift_activity/([1-9][0-9]*)$',admin_views.lift_activity,name = 'lift_activity'),
    url(r'^show_activity_info/admin/([1-9][0-9]*)$', admin_views.admin_show_activity, name='admin_show_activity'),
    url(r'^show_user_info/admin/([1-9][0-9]*)$', admin_views.admin_user_info, name='admin_user_info'),
    url(r'^upgrade_user/admin/([1-9][0-9]*)$', admin_views.upgrade_user, name='upgrade_user'),
    url(r'^degrade_user/admin/([1-9][0-9]*)$', admin_views.degrade_user, name='degrade_user'),
    url(r'^enter_admin$', admin_views.enter_admin, name='enter_admin'),
    url(r'^raise_priority/admin/([1-9][0-9]*)$', admin_views.admin_raise_priority, name='admin_raise_priority'),

    #msg
    url(r'send_message$',msg_views.send_message,name = 'send_message'),
    url(r'unread_message$',msg_views.unread_message,name = 'unread_message'),
    url(r'delete_message/([1-9][0-9]*)$',msg_views.delete_message,name = 'delete_message'),
    url(r'delete_all_messages$',msg_views.delete_all_messages,name = 'delete_all_messages'),
    url(r'set_read/([1-9][0-9]*)$',msg_views.set_read,name = 'set_read'),
    url(r'set_all_read$',msg_views.set_all_read,name = 'set_all_read'),
    url(r'reply_message/([1-9][0-9]*)$',msg_views.reply_message,name = 'reply_message'),
    url(r'send_to_Ta/([1-9][0-9]*)$',msg_views.send_to_Ta,name = 'send_to_Ta'),
]