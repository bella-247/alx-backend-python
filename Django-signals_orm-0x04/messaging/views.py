from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from django.db.models import Q

from .models import User, Message
from .serializers import MessageSerializer


@login_required
def message_create(request):
    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")
        content = request.POST.get("content")
        parent_message_id = request.POST.get("parent_message_id")

        sender = request.user
        receiver = get_object_or_404(User, id=receiver_id)
        parent_message = None
        if parent_message_id:
            parent_message = get_object_or_404(Message, id=parent_message_id)

        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=content,
            parent_message=parent_message,
        )
        serializer = MessageSerializer(message)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_201_CREATED)
    return JsonResponse(
        {"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST
    )


@login_required
def message_edit(request, message_id):
    if request.method in ["PUT", "PATCH"]:
        message = get_object_or_404(Message, id=message_id, sender=request.user)
        new_content = request.PUT.get("content")
        if new_content:
            message.content = new_content
            message.save()
            serializer = MessageSerializer(message)
            return JsonResponse(serializer.data, safe=False)
        return JsonResponse(
            {"error": "Content cannot be empty"}, status=status.HTTP_400_BAD_REQUEST
        )
    return JsonResponse(
        {"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST
    )

def delete_message(request, message_id):
    if request.method == "DELETE":
        message = get_object_or_404(
            Message, Q(sender=request.user) | Q(receiver=request.user), id=message_id
        )
        message.delete()
        return JsonResponse(
            {"message": "Message deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )
    return JsonResponse(
        {"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST
    )

def message_mark_read(request, message_id):
    if request.method == "POST":
        message = get_object_or_404(Message, id=message_id, receiver=request.user)
        message.read = True
        message.save()
        return JsonResponse(
            {"message": "Message marked as read"}, status=status.HTTP_200_OK
        )
    return JsonResponse(
        {"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST
    )

def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    serializer = MessageSerializer(message)
    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


@login_required
@cache_page(60)  # Cache the view for 1 minute
def message_list(request):
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by("-timestamp")
    serializer = MessageSerializer(messages, many=True)
    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


@login_required
def unread_messages(request):
    unread_msgs = Message.unread.for_user(request.user)
    serializer = MessageSerializer(unread_msgs, many=True)
    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


@login_required
def delete_user(request):
    if request.method == "DELETE":
        request.user.delete()
        return JsonResponse(
            {"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )
    return JsonResponse(
        {"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST
    )
