from django.conf import settings
from django.db import models
from django.utils import timezone

from academics.models import Classroom


class Event(models.Model):
    """School calendar events."""

    class EventType(models.TextChoices):
        HOLIDAY = 'HOLIDAY', 'Holiday'
        EXAM = 'EXAM', 'Exam'
        SPORTS = 'SPORTS', 'Sports Event'
        CULTURAL = 'CULTURAL', 'Cultural Event'
        MEETING = 'MEETING', 'Meeting'
        WORKSHOP = 'WORKSHOP', 'Workshop'
        OTHER = 'OTHER', 'Other'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EventType.choices, default=EventType.OTHER)
    
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    location = models.CharField(max_length=200, blank=True)
    
    # Target audience
    all_school = models.BooleanField(default=True, help_text='Event for entire school')
    target_classrooms = models.ManyToManyField(
        Classroom,
        blank=True,
        related_name='events',
        help_text='Specific classes for this event'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date', 'start_time']
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['event_type']),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_date})"

    @property
    def is_upcoming(self):
        """Check if event is in the future."""
        return self.start_date >= timezone.now().date()

    @property
    def is_today(self):
        """Check if event is today."""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    @property
    def duration_days(self):
        """Calculate event duration in days."""
        return (self.end_date - self.start_date).days + 1
