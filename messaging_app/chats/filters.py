import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    """
    Custom filters for the Message model.
    """

    # Filter messages by sender username (case-insensitive contains search)
    sender = django_filters.CharFilter(field_name="sender__username", lookup_expr="icontains")

    # Filter messages belonging to a specific conversation (by UUID)
    conversation = django_filters.UUIDFilter(field_name="conversation__id")

    # Filter messages sent after a given datetime
    sent_after = django_filters.DateTimeFilter(field_name="sent_at", lookup_expr="gte")

    # Filter messages sent before a given datetime
    sent_before = django_filters.DateTimeFilter(field_name="sent_at", lookup_expr="lte")

    # Search inside the message body (case-insensitive)
    search = django_filters.CharFilter(field_name="message_body", lookup_expr="icontains")

    class Meta:
        model = Message
        fields = ["sender", "conversation", "sent_after", "sent_before", "search"]
