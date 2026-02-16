from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
	"""Custom user model with an explicit role for authorization flows."""

	class Role(models.TextChoices):
		ADMIN = 'ADMIN', 'Administrator'
		STAFF = 'STAFF', 'Staff'
		TEACHER = 'TEACHER', 'Teacher'
		STUDENT = 'STUDENT', 'Student'
		GUARDIAN = 'GUARDIAN', 'Guardian / Parent'

	role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)

	@property
	def display_name(self) -> str:
		return self.get_full_name() or self.username

	def __str__(self) -> str:
		return f"{self.display_name} ({self.get_role_display()})"
