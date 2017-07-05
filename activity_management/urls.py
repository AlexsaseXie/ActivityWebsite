from django.conf.urls import url
from . import views
from . import auth_views
from . import user_views
from . import admin_views

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
    url(r'apply_activity$',views.apply_activity,name = 'apply_activity'),
    url(r'show_activity/([1-9][0-9]*)$',views.show_activity,name = 'show_activity'),
    url(r'join_activity/([1-9][0-9]*)$', views.join_activity,name='join_activity'),
    url(r'quit_activity/([1-9][0-9]*)$',views.quit_activity,name = 'quit_activity'),
    url(r'join_activity_list/([1-9][0-9]*)$',views.join_actvity_list,name = 'join_activity_list'),
    url(r'cancel_activity_join/([1-9][0-9]*)$',views.cancel_activity_join,name = 'cancel_activity_join'),
    url(r'clear_activity_join/([1-9][0-9]*)$',views.clear_activity_join,name = 'clear_activity_join'),
    url(r'change_activity_info/([1-9][0-9]*)$',views.change_activity_info,name = 'change_activity_info'),
    url(r'cancel_activity/([1-9][0-9]*)$',views.cancel_activity,name = 'cancel_activity'),
    url(r'resume_activity/([1-9][0-9]*)$',views.resume_activity,name = 'resume_activity'),
    #url(r'user_info$', user_views.user_info, name='user_info'),
    url(r'^multi_apply_submit$', views.multi_apply_submit, name='multi_apply_submit'),
    url(r'show_search_activities$', views.show_search_activities, name='show_search_activities'),

    url(r'show_user_applied_activities/([1-9][0-9]*)$',views.show_user_applied_activities,name = 'show_user_applied_activities'),
    url(r'show_user_joined_activities$',views.show_user_joined_activities,name = 'show_user_joined_activities'),

    #admin
    url(r'admin_home$', admin_views.admin_home, name='admin_home'),
    url(r'ban_activity/([1-9][0-9]*)$',admin_views.ban_activity,name = 'ban_activity'),
    url(r'lift_activity/([1-9][0-9]*)$',admin_views.lift_activity,name = 'lift_activity'),
    url(r'^show_user_info/admin/([1-9][0-9]*)$', admin_views.admin_user_info, name='admin_user_info'),
    url(r'^upgrade_user/admin/([1-9][0-9]*)$', admin_views.upgrade_user, name='upgrade_user'),
    url(r'^degrade_user/admin/([1-9][0-9]*)$', admin_views.degrade_user, name='degrade_user'),
    url(r'^enter_admin$', admin_views.enter_admin, name='enter_admin'),

    #msg
    url(r'send_message$',views.send_message,name = 'send_message'),
    url(r'unread_message$',views.unread_message,name = 'unread_message'),
]