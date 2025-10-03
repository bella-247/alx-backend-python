from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chats.permissions import IsParticipantOfConversation

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .filters import MessageFilter
from .pagination import MessagePagination


# CRUD for Conversation
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def conversation_list_create(request):
    """List all conversations for user, or create a new one."""
    if request.method == "GET":
        conversations = Conversation.objects.filter(participants=request.user)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = ConversationSerializer(data=request.data)
        if serializer.is_valid():
            conversation = serializer.save()
            # conversation.participants.add(request.user)
            return Response(
                ConversationSerializer(conversation).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def conversation_detail(request, conversation_id):
    """Retrieve, update, or delete a conversation."""
    try:
        conversation = Conversation.objects.get(conversation_id=conversation_id)
    except Conversation.DoesNotExist:
        return Response(
            {"detail": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND
        )
    if not IsParticipantOfConversation().has_object_permission(
        request.user, None, conversation
    ):
        return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        serializer = ConversationSerializer(
            conversation, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CRUD for Message
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def message_list_create(request, conversation_id=None):
    """List all messages or create a new one (optionally filtered by conversation)."""
    # If conversation_id is provided, ensure user is a participant
    if conversation_id:
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {"detail": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not IsParticipantOfConversation().has_object_permission(
            request.user, None, conversation
        ):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        messages = Message.objects.filter(
            conversation__conversation_id=conversation_id
        )
        # --- Filtering ---
        filterset = MessageFilter(request.GET, queryset=messages)
        if filterset.is_valid():
            messages = filterset.qs

        # --- Pagination ---
        paginator = MessagePagination()
        paginated_messages = paginator.paginate_queryset(messages, request)

        # Serialize the paginated messages
        serializer = MessageSerializer(paginated_messages, many=True)
        return paginator.get_paginated_response(serializer.data)

    elif request.method == "POST":
        data = request.data.copy()
        data["conversation"] = str(conversation_id) 
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def message_detail(request, message_id):
    """Retrieve, update, or delete a message."""
    try:
        message = Message.objects.get(message_id=message_id)
    except Message.DoesNotExist:
        return Response(
            {"detail": "Message not found."}, status=status.HTTP_404_NOT_FOUND
        )
    
    # --- Permission Check ---
    conversation_permission = IsParticipantOfConversation()
    if (
        request.user != message.sender
        and not conversation_permission.has_object_permission(request.user, None, message.conversation)
    ):
        return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == "GET":
        serializer = MessageSerializer(message)
        return Response(serializer.data)
    
    elif request.method in ["PUT", "PATCH"]:
        serializer = MessageSerializer(
            message, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "DELETE":
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
