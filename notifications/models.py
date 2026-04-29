from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    """System notifications for users."""
    
    NOTIFICATION_TYPES = [
        ('MESSAGE', 'New Message'),
        ('ASSIGNMENT', 'New Assignment'),
        ('ANNOUNCEMENT', 'New Announcement'),
        ('GRADE', 'Grade Posted'),
        ('ATTENDANCE', 'Attendance Alert'),
        ('CALENDAR', 'Calendar Event'),
        ('SYSTEM', 'System Notification'),
    ]
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Optional link to take action
    action_url = models.CharField(max_length=500, blank=True)
    action_text = models.CharField(max_length=50, blank=True)
    
    # Related object (generic)
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class UserNotificationSetting(models.Model):
    """User preferences for notifications."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )
    
    # Email notifications
    email_new_message = models.BooleanField(default=True)
    email_new_assignment = models.BooleanField(default=True)
    email_new_announcement = models.BooleanField(default=True)
    email_grade_posted = models.BooleanField(default=True)
    
    # In-app notifications
    notify_new_message = models.BooleanField(default=True)
    notify_new_assignment = models.BooleanField(default=True)
    notify_new_announcement = models.BooleanField(default=True)
    notify_grade_posted = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'User Notification Setting'
        verbose_name_plural = 'User Notification Settings'
    
    def __str__(self):
        return f"Notification settings for {self.user.username}"
