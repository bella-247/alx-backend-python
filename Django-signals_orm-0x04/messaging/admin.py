from django.contrib import admin
from .models import User, Message, Notifications, MessageHistory
# Register your models here.

admin.site.register(User)
admin.site.register(Message)
admin.site.register(Notifications)
admin.site.register(MessageHistory)
