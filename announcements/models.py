from django.conf import settings
from django.db import models
from django.utils import timezone

from academics.models import Classroom


class Announcement(models.Model):
    """School announcements and notices."""

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        NORMAL = 'NORMAL', 'Normal'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    class Audience(models.TextChoices):
        ALL = 'ALL', 'Everyone'
        STUDENTS = 'STUDENTS', 'Students Only'
        TEACHERS = 'TEACHERS', 'Teachers Only'
        GUARDIANS = 'GUARDIANS', 'Guardians Only'
        STAFF = 'STAFF', 'Staff Only'

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='announcements'
    )
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    audience = models.CharField(max_length=20, choices=Audience.choices, default=Audience.ALL)
    
    # Optional: target specific classes
    target_classrooms = models.ManyToManyField(
        Classroom,
        blank=True,
        related_name='announcements',
        help_text='Leave empty to show to all classes'
    )
    
    pinned = models.BooleanField(default=False, help_text='Pin to top of announcements')
    published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text='Announcement will be hidden after this date')

    class Meta:
        ordering = ['-pinned', '-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['published', 'audience']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        """Check if announcement has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def is_active(self):
        """Check if announcement is currently active."""
        return self.published and not self.is_expired


class AnnouncementAttachment(models.Model):
    """File attachments for announcements."""
    
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='announcements/%Y/%m/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename


class AnnouncementView(models.Model):
    """Track who has viewed each announcement."""
    
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='views'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='announcement_views'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['announcement', 'user']]
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.user.username} viewed {self.announcement.title}"
