from django import forms
from .models import UserProfile, Activity, Join, Msg

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ('name', 'type','description','capacity','start_time','end_time','place')

class DateForm(forms.Form):
    date = forms.DateField(label = 'date')


class ActivitySearchForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ('name','type','place','state')
        date = forms.DateField(label = 'date')

class MessageForm(forms.Form):
    receive_user_name = forms.CharField(max_length=100,label='发送对象')
    title = forms.CharField(max_length=100,label='消息标题')
    content = forms.CharField(max_length = 300 ,label = '消息内容')