from django import template
from activity_management.models import UserProfile,Msg,Activity,Join

register = template.Library()

@register.simple_tag
def my_unread_count(user_id):
    count = UserProfile.count_user_unread_msgs(UserProfile(), user_id=user_id, state=0)
    return  count
