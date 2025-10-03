from typing import Any
from rest_framework.permissions import BasePermission

class IsParticipantOfConversation(BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool: # pyright: ignore[reportIncompatibleMethodOverride]
        if not request.user or not request.user.is_authenticated:
            return False

        if not hasattr(obj, 'participants'):
            return False

        return obj.participants.filter(id=request.user.id).exists()