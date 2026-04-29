from django.conf import settings
from django.db import models

from academics.models import Classroom, Subject
from students.models import Student


class AttendanceRecord(models.Model):
	class Status(models.TextChoices):
		PRESENT = 'PRESENT', 'Present'
		ABSENT = 'ABSENT', 'Absent'
		LATE = 'LATE', 'Late'
		EXCUSED = 'EXCUSED', 'Excused'

	student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
	classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='attendance_records')
	subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendance_records')
	date = models.DateField()
	status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
	notes = models.TextField(blank=True)
	recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='attendance_records')
	recorded_at = models.DateTimeField(auto_now_add=True)
	digest_sent_at = models.DateTimeField(null=True, blank=True, db_index=True)

	class Meta:
		ordering = ['-date', 'student__admission_number']
		unique_together = ('student', 'subject', 'date')

	def __str__(self) -> str:
		return f"{self.student.full_name} - {self.date} ({self.get_status_display()})"


class ReportTemplate(models.Model):
	"""Saved report templates for custom attendance reports."""
	
	class Grouping(models.TextChoices):
		NONE = 'NONE', 'No Grouping'
		STUDENT = 'STUDENT', 'By Student'
		CLASSROOM = 'CLASSROOM', 'By Classroom'
		SUBJECT = 'SUBJECT', 'By Subject'
		DATE = 'DATE', 'By Date'
	
	class Sorting(models.TextChoices):
		DATE_ASC = 'DATE_ASC', 'Date (Oldest First)'
		DATE_DESC = 'DATE_DESC', 'Date (Newest First)'
		STUDENT_ASC = 'STUDENT_ASC', 'Student Name (A-Z)'
		STUDENT_DESC = 'STUDENT_DESC', 'Student Name (Z-A)'
		STATUS_ASC = 'STATUS_ASC', 'Status (A-Z)'
		STATUS_DESC = 'STATUS_DESC', 'Status (Z-A)'
	
	name = models.CharField(max_length=120, help_text='Template name for easy identification')
	description = models.TextField(blank=True, help_text='Optional description of this report template')
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='report_templates'
	)
	
	# Selected fields to include in report
	fields = models.JSONField(
		default=list,
		help_text='List of field names to include in the report'
	)
	
	# Default filters
	filters = models.JSONField(
		default=dict,
		help_text='Default filter values (date_from, date_to, classroom_id, etc.)'
	)
	
	# Display options
	grouping = models.CharField(
		max_length=20,
		choices=Grouping.choices,
		default=Grouping.NONE,
		blank=True
	)
	sorting = models.CharField(
		max_length=20,
		choices=Sorting.choices,
		default=Sorting.DATE_DESC
	)
	
	# Sharing
	is_shared = models.BooleanField(
		default=False,
		help_text='Allow other admin users to use this template'
	)
	
	# Timestamps
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['created_by', '-created_at']),
		]
	
	def __str__(self) -> str:
		return f"{self.name} (by {self.created_by.get_full_name() or self.created_by.username})"


class NotificationPreference(models.Model):
	"""Email notification preferences for guardians/parents."""
	
	class NotificationMode(models.TextChoices):
		IMMEDIATE = 'IMMEDIATE', 'Immediate (real-time)'
		DAILY_DIGEST = 'DAILY_DIGEST', 'Daily Digest (once per day)'
		OFF = 'OFF', 'Off (no notifications)'
	
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='notification_preferences'
	)
	mode = models.CharField(
		max_length=20,
		choices=NotificationMode.choices,
		default=NotificationMode.IMMEDIATE
	)
	notify_absent = models.BooleanField(default=True, help_text='Send notification when student is marked absent')
	notify_late = models.BooleanField(default=True, help_text='Send notification when student is marked late')
	notify_excused = models.BooleanField(default=False, help_text='Send notification when student is marked excused')
	email = models.EmailField(blank=True, help_text='Override email (if different from account email)')
	is_enabled = models.BooleanField(default=True, help_text='Master switch for all notifications')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		verbose_name = 'Notification Preference'
		verbose_name_plural = 'Notification Preferences'
	
	def __str__(self) -> str:
		return f"{self.user.display_name} - {self.get_mode_display()}"
	
	def get_email(self):
		"""Get the email address to use for notifications."""
		return self.email or self.user.email


class EmailLog(models.Model):
	"""Log of sent email notifications for tracking and debugging."""
	
	class Status(models.TextChoices):
		PENDING = 'PENDING', 'Pending'
		SENT = 'SENT', 'Sent'
		FAILED = 'FAILED', 'Failed'
	
	recipient = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		related_name='email_logs'
	)
	recipient_email = models.EmailField()
	subject = models.CharField(max_length=255)
	attendance_record = models.ForeignKey(
		'AttendanceRecord',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='email_logs'
	)
	status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
	error_message = models.TextField(blank=True)
	sent_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering = ['-sent_at']
	
	def __str__(self) -> str:
		return f"{self.recipient_email} - {self.subject} ({self.get_status_display()})"
