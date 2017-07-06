from django import forms
from .models import UserProfile, Activity, Join, Msg
from django.contrib.admin import widgets

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        widgets = {'start_time':widgets.AdminSplitDateTime,'end_time':widgets.AdminSplitDateTime}
        fields = ('name', 'type','description','capacity','start_time','end_time','place')


class DateForm(forms.Form):
    date = forms.DateField(label = 'date',widget=widgets.AdminDateWidget())


class ActivitySearchForm(forms.Form):
    search_date = forms.DateField(label='日期',required= False,widget= widgets.AdminDateWidget())
    name = forms.CharField(label='名称',required= False)
    type = forms.CharField(label='类型',required= False)
    place = forms.CharField(label='地点',required= False)
    state_choices = (('',''),(1,'申请中'),(2,'被创建者取消'),(3,'被管理员禁用'),(4,'安排未中'),(5,'等待举办'),(6,'完成'))
    state = forms.ChoiceField(choices= state_choices,label='状态',required= False)


class MessageForm(forms.Form):
    receive_user_name = forms.CharField(max_length=100,label='发送对象')
    title = forms.CharField(max_length=100,label='消息标题')
    content = forms.CharField(max_length = 300 ,label = '消息内容')