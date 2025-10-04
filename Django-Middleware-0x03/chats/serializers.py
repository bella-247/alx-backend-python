from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """

    class Meta:
        model = User
        fields = [
            "user_id",
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
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "message_body", "sent_at"]

    def validate_message_body(self, value):
        """Ensure message body is not empty or only whitespace."""
        if not value or not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    Handles nested representation of participants and messages.
    """

    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(
        many=True, read_only=True
    )  # nest messages within conversation
    # include a computed field for the most recent message in the conversation
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "participants", "created_at", "messages", "last_message"]

    def get_last_message(self, obj):
        """Return the serialized last message or None if no messages exist."""
        last = obj.messages.order_by('-sent_at').first()
        if not last:
            return None
        return MessageSerializer(last).data
