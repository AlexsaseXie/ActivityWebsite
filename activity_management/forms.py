from django import forms
from .models import UserProfile, Activity, Join, Msg

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ('name', 'type','description','capacity','start_time','end_time','place')

class DateForm(forms.Form):
    date = forms.DateField(label = 'date')