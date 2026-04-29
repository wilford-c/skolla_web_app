"""Signal handlers for creating notifications."""
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from messaging.models import Message
from assignments.models import Assignment
from announcements.models import Announcement
from .models import Notification
from .realtime import push_unread_count


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """Create notification when a new message is sent."""
    if created:
        # Notify all participants except the sender
        conversation = instance.conversation
        recipients = conversation.participants.exclude(id=instance.sender.id)
        
        for recipient in recipients:
            Notification.objects.create(
                recipient=recipient,
                notification_type='MESSAGE',
                title=f'New message from {instance.sender.display_name}',
                message=f'{instance.sender.display_name}: {instance.content[:100]}...' if len(instance.content) > 100 else instance.content,
                action_url=reverse('messaging:conversation', kwargs={'pk': conversation.pk}),
                action_text='View conversation',
                related_object_id=instance.id,
                related_object_type='message'
            )


@receiver(post_save, sender=Notification)
def push_badge_update_on_notification_save(sender, instance, **kwargs):
    """Push unread badge updates whenever a notification changes."""
    push_unread_count(instance.recipient_id)


@receiver(post_delete, sender=Notification)
def push_badge_update_on_notification_delete(sender, instance, **kwargs):
    """Push unread badge updates whenever a notification is removed."""
    push_unread_count(instance.recipient_id)


@receiver(post_save, sender=Assignment)
def create_assignment_notification(sender, instance, created, **kwargs):
    """Create notification when a new assignment is published."""
    if created and instance.status == 'PUBLISHED':
        # Get all students in the classroom
        from students.models import Student
        students = Student.objects.filter(classroom=instance.classroom)
        
        for student in students:
            if student.user:
                Notification.objects.create(
                    recipient=student.user,
                    notification_type='ASSIGNMENT',
                    title=f'New assignment: {instance.title}',
                    message=f'{instance.teacher.display_name} posted a new assignment for {instance.subject.name}. Due: {instance.due_date.strftime("%b %d, %Y")}',
                    action_url=reverse('assignments:detail', kwargs={'pk': instance.pk}),
                    action_text='View assignment',
                    related_object_id=instance.id,
                    related_object_type='assignment'
                )


@receiver(post_save, sender=Announcement)
def create_announcement_notification(sender, instance, created, **kwargs):
    """Create notification when a new announcement is published."""
    if created and instance.published:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Determine recipients based on audience
        if instance.audience == 'ALL':
            recipients = User.objects.all()
        elif instance.audience == 'STUDENTS':
            recipients = User.objects.filter(role='STUDENT')
        elif instance.audience == 'TEACHERS':
            recipients = User.objects.filter(role='TEACHER')
        elif instance.audience == 'GUARDIANS':
            recipients = User.objects.filter(role='GUARDIAN')
        elif instance.audience == 'STAFF':
            recipients = User.objects.filter(role__in=['STAFF', 'ADMIN'])
        else:
            return
        
        # Exclude the author
        recipients = recipients.exclude(id=instance.author.id)
        
        for recipient in recipients:
            Notification.objects.create(
                recipient=recipient,
                notification_type='ANNOUNCEMENT',
                title=f'New announcement: {instance.title}',
                message=instance.content[:200] + '...' if len(instance.content) > 200 else instance.content,
                action_url=reverse('announcements:detail', kwargs={'pk': instance.pk}),
                action_text='Read announcement',
                related_object_id=instance.id,
                related_object_type='announcement'
            )
