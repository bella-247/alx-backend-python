from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from django.db.models import Q
from .models import Message, Notification, User, MessageHistory

@receiver(post_save, sender=Message)
def notify_message_creation(sender, instance, created, **kwargs):
    if created:
        print(f'New message created: {instance}')
        Notification.objects.create(user=instance.receiver, message=instance)

# Example of pre_save signal to log message updates
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if not instance.pk:
        return  # Skip if it's a new message
    try:
        old_instance = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return  # Skip if the old instance doesn't exist

    if old_instance.content != instance.content:
        MessageHistory.objects.create(message=instance, old_content=old_instance.content)
        print(f'Old message content: {old_instance.content}')
        

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    Message.objects.filter(Q(sender=instance) | Q(receiver=instance)).delete()
    Notification.objects.filter(user=instance).delete()
    MessageHistory.objects.filter(message__sender=instance).delete()
    print(f'All messages, history and notifications for user {instance} have been deleted.')