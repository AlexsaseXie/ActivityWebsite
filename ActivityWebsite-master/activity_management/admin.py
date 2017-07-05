from django.contrib import admin
from .models import UserProfile, Activity, Join, Msg

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Activity)
admin.site.register(Join)
admin.site.register(Msg)
