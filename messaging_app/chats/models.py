import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    """
    Custom user model for the messaging app.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    ROLE_CHOICES = (
        ('guest', "Guest"),
        ('host', "Host"),
        ('admin', "Admin"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')

    def __str__(self):
        return self.username


class Conversation(models.Model):
    """
    Represents a single message within a conversation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"
    
class Message(models.Model):
    """
    Represents a single message within a conversation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} at {self.sent_at}"
    
    class Meta:
        ordering = ['-sent_at']