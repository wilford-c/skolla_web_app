from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from academics.models import Classroom, Subject
from attendance.models import AttendanceRecord, EmailLog, NotificationPreference
from students.models import Student


class AttendanceDailyDigestCommandTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.guardian = User.objects.create_user(
			username='guardian_digest',
			email='guardian.digest@example.com',
			password='testpass123',
			role=User.Role.GUARDIAN,
			first_name='Daily',
			last_name='Guardian',
		)
		self.teacher = User.objects.create_user(
			username='teacher_digest',
			email='teacher.digest@example.com',
			password='testpass123',
			role=User.Role.TEACHER,
		)

		self.classroom = Classroom.objects.create(name='Grade 7A', code='G7A', homeroom_teacher=self.teacher)
		self.subject = Subject.objects.create(name='Mathematics', code='MATH7A', classroom=self.classroom, teacher=self.teacher)

		self.student_one = Student.objects.create(
			admission_number='STU-0001',
			first_name='Alex',
			last_name='One',
			date_of_birth='2012-01-01',
			guardian_name='Daily Guardian',
			guardian_user=self.guardian,
			status=Student.Status.ACTIVE,
		)
		self.student_two = Student.objects.create(
			admission_number='STU-0002',
			first_name='Blair',
			last_name='Two',
			date_of_birth='2012-02-02',
			guardian_name='Daily Guardian',
			guardian_user=self.guardian,
			status=Student.Status.ACTIVE,
		)

		self.preferences = NotificationPreference.objects.create(
			user=self.guardian,
			mode=NotificationPreference.NotificationMode.DAILY_DIGEST,
			notify_absent=True,
			notify_late=True,
			notify_excused=False,
			is_enabled=True,
		)

	def test_command_sends_one_digest_per_guardian_and_marks_records(self):
		yesterday = timezone.localdate() - timedelta(days=1)
		today = timezone.localdate()

		record_absent = AttendanceRecord.objects.create(
			student=self.student_one,
			classroom=self.classroom,
			subject=self.subject,
			date=yesterday,
			status=AttendanceRecord.Status.ABSENT,
			recorded_by=self.teacher,
		)
		record_late = AttendanceRecord.objects.create(
			student=self.student_two,
			classroom=self.classroom,
			subject=self.subject,
			date=yesterday,
			status=AttendanceRecord.Status.LATE,
			recorded_by=self.teacher,
		)
		record_excused = AttendanceRecord.objects.create(
			student=self.student_one,
			classroom=self.classroom,
			subject=None,
			date=yesterday,
			status=AttendanceRecord.Status.EXCUSED,
			recorded_by=self.teacher,
		)
		record_outside_period = AttendanceRecord.objects.create(
			student=self.student_two,
			classroom=self.classroom,
			subject=None,
			date=today,
			status=AttendanceRecord.Status.ABSENT,
			recorded_by=self.teacher,
		)

		call_command('send_attendance_daily_digest')

		self.assertEqual(len(mail.outbox), 1)
		email = mail.outbox[0]
		self.assertIn('Daily Attendance Digest', email.subject)
		self.assertIn(self.student_one.full_name, email.body)
		self.assertIn(self.student_two.full_name, email.body)
		self.assertIn('Absent', email.body)
		self.assertIn('Late', email.body)

		record_absent.refresh_from_db()
		record_late.refresh_from_db()
		record_excused.refresh_from_db()
		record_outside_period.refresh_from_db()

		self.assertIsNotNone(record_absent.digest_sent_at)
		self.assertIsNotNone(record_late.digest_sent_at)
		self.assertIsNone(record_excused.digest_sent_at)
		self.assertIsNone(record_outside_period.digest_sent_at)

		self.assertEqual(
			EmailLog.objects.filter(recipient=self.guardian, status=EmailLog.Status.SENT).count(),
			1,
		)

	def test_command_prevents_duplicate_digests(self):
		yesterday = timezone.localdate() - timedelta(days=1)

		record_absent = AttendanceRecord.objects.create(
			student=self.student_one,
			classroom=self.classroom,
			subject=self.subject,
			date=yesterday,
			status=AttendanceRecord.Status.ABSENT,
			recorded_by=self.teacher,
		)

		call_command('send_attendance_daily_digest')
		call_command('send_attendance_daily_digest')

		record_absent.refresh_from_db()
		self.assertIsNotNone(record_absent.digest_sent_at)
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(
			EmailLog.objects.filter(recipient=self.guardian, status=EmailLog.Status.SENT).count(),
			1,
		)
