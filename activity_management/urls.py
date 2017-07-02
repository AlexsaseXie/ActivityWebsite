from django.conf.urls import url
from . import views
from . import auth_views

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
    url(r'change_info$', views.change_info, name='change_info'),
    url(r'change_info/submit$', views.change_info_submit, name='change_info_submit'),

]