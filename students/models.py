from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.db.models import Q
from django.utils import timezone


class Student(models.Model):
	class Status(models.TextChoices):
		ACTIVE = 'ACTIVE', 'Active'
		INACTIVE = 'INACTIVE', 'Inactive'
		GRADUATED = 'GRADUATED', 'Graduated'

	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		related_name='student_profile',
		blank=True,
		null=True,
	)
	admission_number = models.CharField(max_length=32, unique=True)
	first_name = models.CharField(max_length=150)
	last_name = models.CharField(max_length=150)
	date_of_birth = models.DateField()
	current_classroom = models.ForeignKey(
		'academics.Classroom',
		on_delete=models.SET_NULL,
		related_name='students',
		blank=True,
		null=True,
		help_text='Current primary classroom/section.',
	)
	guardian_name = models.CharField(max_length=255)
	guardian_user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		related_name='guardian_students',
		blank=True,
		null=True,
		help_text='Optional portal account for guardians/parents.',
	)
	contact_email = models.EmailField(blank=True)
	contact_phone = models.CharField(max_length=32, blank=True)
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
	enrolled_on = models.DateField(auto_now_add=True)

	class Meta:
		ordering = ['admission_number']

	@property
	def full_name(self) -> str:
		return f"{self.first_name} {self.last_name}".strip()

	def __str__(self) -> str:
		return f"{self.full_name} ({self.admission_number})"

	def save(self, *args, **kwargs):
		sync_enrollment = kwargs.pop('sync_enrollment', True)
		enrollment_actor = kwargs.pop('enrollment_actor', None)
		enrollment_note = kwargs.pop('enrollment_note', '')
		enrollment_effective_date = kwargs.pop('enrollment_effective_date', None)

		super().save(*args, **kwargs)

		if sync_enrollment:
			self.sync_enrollment_history(
				actor=enrollment_actor,
				note=enrollment_note,
				effective_date=enrollment_effective_date,
			)

	def sync_enrollment_history(self, actor=None, note: str = '', effective_date=None):
		effective_date = effective_date or timezone.localdate()
		current_active = Enrollment.objects.filter(
			student=self,
			status=Enrollment.Status.ACTIVE,
			end_date__isnull=True,
		).order_by('start_date').first()
		if current_active and effective_date < current_active.start_date:
			effective_date = current_active.start_date

		if self.status == self.Status.GRADUATED:
			self._close_active_enrollments(
				status=Enrollment.Status.COMPLETED,
				effective_date=effective_date,
			)
			return

		if self.status == self.Status.INACTIVE:
			self._close_active_enrollments(
				status=Enrollment.Status.WITHDRAWN,
				effective_date=effective_date,
			)
			return

		if not self.current_classroom_id:
			self._close_active_enrollments(
				status=Enrollment.Status.WITHDRAWN,
				effective_date=effective_date,
			)
			return

		self._close_active_enrollments(
			status=Enrollment.Status.TRANSFERRED,
			effective_date=effective_date,
			exclude_classroom_id=self.current_classroom_id,
		)

		active_enrollment = Enrollment.objects.filter(
			student=self,
			classroom_id=self.current_classroom_id,
			status=Enrollment.Status.ACTIVE,
			end_date__isnull=True,
		).first()

		if active_enrollment:
			if note:
				normalized_note = note.strip()
				if normalized_note and normalized_note not in (active_enrollment.notes or ''):
					if active_enrollment.notes:
						active_enrollment.notes = f"{active_enrollment.notes}\n{normalized_note}"
					else:
						active_enrollment.notes = normalized_note
					active_enrollment.save(update_fields=['notes', 'updated_at'])
			return

		onboarding_note = (note or '').strip() or 'Initial onboarding enrollment.'
		Enrollment.objects.create(
			student=self,
			classroom_id=self.current_classroom_id,
			start_date=effective_date,
			onboarded_by=(actor if getattr(actor, 'is_authenticated', False) else None),
			notes=onboarding_note,
		)

	def _close_active_enrollments(self, status, effective_date, exclude_classroom_id=None):
		active_enrollments = Enrollment.objects.filter(
			student=self,
			status=Enrollment.Status.ACTIVE,
		)

		if exclude_classroom_id is not None:
			active_enrollments = active_enrollments.exclude(classroom_id=exclude_classroom_id)

		for enrollment in active_enrollments:
			changed = False
			resolved_end_date = effective_date
			if resolved_end_date < enrollment.start_date:
				resolved_end_date = enrollment.start_date

			if enrollment.status != status:
				enrollment.status = status
				changed = True
			if enrollment.end_date != resolved_end_date:
				enrollment.end_date = resolved_end_date
				changed = True

			if changed:
				enrollment.save(update_fields=['status', 'end_date', 'updated_at'])


class Enrollment(models.Model):
	class Status(models.TextChoices):
		ACTIVE = 'ACTIVE', 'Active'
		TRANSFERRED = 'TRANSFERRED', 'Transferred'
		COMPLETED = 'COMPLETED', 'Completed'
		WITHDRAWN = 'WITHDRAWN', 'Withdrawn'

	student = models.ForeignKey(
		Student,
		on_delete=models.CASCADE,
		related_name='enrollments',
	)
	classroom = models.ForeignKey(
		'academics.Classroom',
		on_delete=models.CASCADE,
		related_name='enrollments',
	)
	start_date = models.DateField(default=timezone.localdate)
	end_date = models.DateField(blank=True, null=True)
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
	onboarded_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		related_name='student_enrollments_onboarded',
		blank=True,
		null=True,
	)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-start_date', '-created_at']
		indexes = [
			models.Index(fields=['student', 'status']),
			models.Index(fields=['classroom', 'status']),
			models.Index(fields=['-start_date']),
		]
		constraints = [
			models.UniqueConstraint(
				fields=['student'],
				condition=Q(status='ACTIVE'),
				name='students_unique_active_enrollment_per_student',
			),
			models.CheckConstraint(
				condition=Q(end_date__isnull=True) | Q(end_date__gte=F('start_date')),
				name='students_enrollment_end_date_gte_start_date',
			),
		]

	def clean(self):
		super().clean()
		if self.status == self.Status.ACTIVE and self.end_date is not None:
			raise ValidationError('Active enrollments cannot have an end date.')
		if self.status != self.Status.ACTIVE and self.end_date is None:
			raise ValidationError('Ended enrollments must include an end date.')

	def __str__(self) -> str:
		return f"{self.student.admission_number} -> {self.classroom.code} ({self.get_status_display()})"
