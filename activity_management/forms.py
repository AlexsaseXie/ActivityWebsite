from django import forms
from .models import UserProfile, Activity, Join, Msg

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ('name', 'type','description','capacity','state','start_time','end_time','place','state')