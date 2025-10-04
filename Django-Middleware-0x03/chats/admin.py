from django.contrib import admin
from .models import Conversation, Message, User
# Register your models here.
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("conversation_id", "created_at")
    search_fields = ("participants__username",)
    list_filter = ("created_at",)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("message_id", "conversation", "sender", "sent_at")
    search_fields = ("sender__username", "conversation__id")
    list_filter = ("sent_at",)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "username", "email")
    search_fields = ("username", "email")