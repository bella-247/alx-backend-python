from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
        ]


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    """

    sender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "message_body", "sent_at"]


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    Handles nested representation of participants and messages.
    """

    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(
        many=True, read_only=True
    )  # nest messages within conversation

    class Meta:
        model = Conversation
        fields = ["id", "participants", "created_at", "messages"]
