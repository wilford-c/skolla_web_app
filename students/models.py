from django.conf import settings
from django.db import models


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
