from django.conf import settings
from django.db import models
from django.utils import timezone

from academics.models import Classroom, Subject
from students.models import Student


class Assignment(models.Model):
    """Homework and assignments."""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        CLOSED = 'CLOSED', 'Closed'

    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField(blank=True, help_text='Detailed instructions')
    
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignments_created'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assignments')
    
    assigned_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    max_marks = models.PositiveIntegerField(default=100)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PUBLISHED)
    allow_late_submission = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assigned_date']
        indexes = [
            models.Index(fields=['classroom', 'subject']),
            models.Index(fields=['-due_date']),
        ]

    def __str__(self):
        return f"""{self.title} - {self.classroom.name}"""

    @property
    def is_overdue(self):
        """Check if assignment is past due date."""
        return timezone.now() > self.due_date

    @property
    def days_until_due(self):
        """Calculate days remaining until due date."""
        if self.is_overdue:
            return 0
        delta = self.due_date - timezone.now()
        return delta.days


class AssignmentAttachment(models.Model):
    """File attachments for assignments."""
    
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='assignments/%Y/%m/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename


class Submission(models.Model):
    """Student assignment submissions."""

    class SubmissionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        GRADED = 'GRADED', 'Graded'
        RETURNED = 'RETURNED', 'Returned'

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    content = models.TextField(blank=True, help_text='Text submission')
    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    feedback = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.PENDING
    )
    
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions'
    )

    class Meta:
        unique_together = [['assignment', 'student']]
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['assignment', 'student']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"""{self.student.full_name} - {self.assignment.title}"""

    @property
    def is_late(self):
        """Check if submission was late."""
        return self.submitted_at > self.assignment.due_date

    @property
    def percentage(self):
        """Calculate percentage score."""
        if self.marks_obtained is not None:
            return (self.marks_obtained / self.assignment.max_marks) * 100
        return None


class SubmissionFile(models.Model):
    """File uploads for submissions."""
    
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(upload_to='submissions/%Y/%m/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename

