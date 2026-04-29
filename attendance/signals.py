"""Signal handlers for attendance notifications."""

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone

from .models import AttendanceRecord, EmailLog, NotificationPreference
from .realtime import push_admin_dashboard_update


@receiver(post_save, sender=AttendanceRecord)
def send_attendance_notification(sender, instance, created, **kwargs):
	"""
	Send email notification to guardian when attendance is recorded.
	Only sends for new records (not updates) and for absent/late status.
	"""
	if not created:
		return  # Don't send for updates
	
	# Check if student has a guardian with an email
	student = instance.student
	if not student.guardian_user:
		return
	
	guardian = student.guardian_user
	
	# Check if guardian has email
	if not guardian.email and not (hasattr(guardian, 'notification_preferences') and guardian.notification_preferences.email):
		return
	
	# Get or create notification preferences
	try:
		prefs = guardian.notification_preferences
	except NotificationPreference.DoesNotExist:
		# Create default preferences
		prefs = NotificationPreference.objects.create(user=guardian)
	
	# Check if notifications are enabled
	if not prefs.is_enabled or prefs.mode == NotificationPreference.NotificationMode.OFF:
		return
	
	# Check if we should notify for this status
	should_notify = False
	if instance.status == AttendanceRecord.Status.ABSENT and prefs.notify_absent:
		should_notify = True
	elif instance.status == AttendanceRecord.Status.LATE and prefs.notify_late:
		should_notify = True
	elif instance.status == AttendanceRecord.Status.EXCUSED and prefs.notify_excused:
		should_notify = True
	
	if not should_notify:
		return
	
	# For daily digest mode, we'll skip immediate sending
	# (A management command should be created to send daily digests)
	if prefs.mode == NotificationPreference.NotificationMode.DAILY_DIGEST:
		return
	
	# Send immediate notification
	recipient_email = prefs.get_email()
	subject = f"Attendance Alert: {student.full_name} - {instance.get_status_display()}"
	
	# Prepare context for email template
	context = {
		'guardian_name': guardian.get_full_name() or guardian.username,
		'student': student,
		'record': instance,
		'date': instance.date,
		'status': instance.get_status_display(),
		'classroom': instance.classroom,
		'subject': instance.subject,
		'notes': instance.notes,
		'site_url': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
	}
	
	# Render email content
	html_message = render_to_string('attendance/emails/absence_notification.html', context)
	plain_message = render_to_string('attendance/emails/absence_notification.txt', context)
	
	# Create email log entry
	email_log = EmailLog.objects.create(
		recipient=guardian,
		recipient_email=recipient_email,
		subject=subject,
		attendance_record=instance,
		status=EmailLog.Status.PENDING,
	)
	
	try:
		# Send email
		send_mail(
			subject=subject,
			message=plain_message,
			from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@skola.edu',
			recipient_list=[recipient_email],
			html_message=html_message,
			fail_silently=False,
		)
		
		# Update log
		email_log.status = EmailLog.Status.SENT
		email_log.save()
		
	except Exception as e:
		# Log the error
		email_log.status = EmailLog.Status.FAILED
		email_log.error_message = str(e)
		email_log.save()


@receiver(post_save, sender=AttendanceRecord)
def push_attendance_dashboard_on_save(sender, instance, **kwargs):
	"""Push updated dashboard attendance metrics after saves."""
	push_admin_dashboard_update()


@receiver(post_delete, sender=AttendanceRecord)
def push_attendance_dashboard_on_delete(sender, instance, **kwargs):
	"""Push updated dashboard attendance metrics after deletes."""
	push_admin_dashboard_update()
