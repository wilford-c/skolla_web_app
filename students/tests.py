from datetime import date
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from academics.models import Classroom

from .models import Enrollment, Student


User = get_user_model()


class EnrollmentLifecycleTests(TestCase):
	def setUp(self):
		self.admin = User.objects.create_user(
			username='admin_students',
			password='pass1234',
			role=User.Role.ADMIN,
		)
		self.classroom_a = Classroom.objects.create(name='Grade 7 A', code='G7A')
		self.classroom_b = Classroom.objects.create(name='Grade 7 B', code='G7B')

		self.student = Student(
			admission_number='ST-ENR-001',
			first_name='Nora',
			last_name='Moyo',
			date_of_birth='2011-02-10',
			current_classroom=self.classroom_a,
			guardian_name='Parent One',
			status=Student.Status.ACTIVE,
		)
		self.student.save(enrollment_actor=self.admin)

	def test_student_creation_creates_active_enrollment(self):
		enrollment = Enrollment.objects.get(student=self.student)
		self.assertEqual(enrollment.classroom, self.classroom_a)
		self.assertEqual(enrollment.status, Enrollment.Status.ACTIVE)
		self.assertIsNone(enrollment.end_date)

	def test_classroom_transfer_closes_previous_and_creates_new_active_enrollment(self):
		active_enrollment = Enrollment.objects.get(student=self.student, classroom=self.classroom_a)
		effective_date = active_enrollment.start_date + timedelta(days=7)

		self.student.current_classroom = self.classroom_b
		self.student.save(
			enrollment_actor=self.admin,
			enrollment_note='Transferred by registrar.',
			enrollment_effective_date=effective_date,
		)

		old_enrollment = Enrollment.objects.get(student=self.student, classroom=self.classroom_a)
		new_enrollment = Enrollment.objects.get(student=self.student, classroom=self.classroom_b)

		self.assertEqual(old_enrollment.status, Enrollment.Status.TRANSFERRED)
		self.assertEqual(old_enrollment.end_date, effective_date)
		self.assertEqual(new_enrollment.status, Enrollment.Status.ACTIVE)
		self.assertEqual(new_enrollment.start_date, effective_date)

	def test_graduating_student_closes_active_enrollment(self):
		effective_date = date(2026, 11, 25)

		self.student.status = Student.Status.GRADUATED
		self.student.save(
			enrollment_actor=self.admin,
			enrollment_note='Graduated and exited campus.',
			enrollment_effective_date=effective_date,
		)

		enrollment = Enrollment.objects.get(student=self.student, classroom=self.classroom_a)
		self.assertEqual(enrollment.status, Enrollment.Status.COMPLETED)
		self.assertEqual(enrollment.end_date, effective_date)
		self.assertFalse(
			Enrollment.objects.filter(student=self.student, status=Enrollment.Status.ACTIVE).exists()
		)

	def test_transfer_view_updates_student_and_enrollment_history(self):
		self.client.force_login(self.admin)
		active_enrollment = Enrollment.objects.get(student=self.student, classroom=self.classroom_a)
		effective_date = active_enrollment.start_date + timedelta(days=10)

		response = self.client.post(
			reverse('students:transfer', args=[self.student.pk]),
			{
				'new_classroom': self.classroom_b.pk,
				'effective_date': effective_date.isoformat(),
				'note': 'Promoted mid-term.',
			},
		)

		self.assertEqual(response.status_code, 302)
		self.student.refresh_from_db()

		self.assertEqual(self.student.current_classroom, self.classroom_b)
		self.assertTrue(
			Enrollment.objects.filter(
				student=self.student,
				classroom=self.classroom_b,
				status=Enrollment.Status.ACTIVE,
				start_date=effective_date,
			).exists()
		)
