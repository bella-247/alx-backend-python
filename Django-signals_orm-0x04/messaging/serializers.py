from rest_framework import serializers
from .models import User, Message, Notifications, MessageHistory

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio']
        read_only_fields = ["id", "username", "email"]
        
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'read', 'parent_message']
        read_only_fields = ["id", "timestamp", "sender"]
        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = ['id', 'user', 'message', 'read', 'timestamp']
        read_only_fields = ["id", "user", 'timestamp']
        
class MessageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageHistory
        fields = ['id', 'message', 'edited_at', 'old_content']
        read_only_fields = ["id", 'edited_at', 'old_content']