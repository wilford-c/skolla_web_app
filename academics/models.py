from django.conf import settings
from django.db import models


class Classroom(models.Model):
	name = models.CharField(max_length=120)
	code = models.CharField(max_length=20, unique=True)
	homeroom_teacher = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		related_name='homeroom_classes',
		null=True,
		blank=True,
	)
	description = models.TextField(blank=True)

	class Meta:
		ordering = ['code']

	def __str__(self) -> str:
		return f"{self.name} ({self.code})"


class Subject(models.Model):
	name = models.CharField(max_length=120)
	code = models.CharField(max_length=20, unique=True)
	classroom = models.ForeignKey(
		Classroom,
		on_delete=models.CASCADE,
		related_name='subjects',
	)
	teacher = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		related_name='subjects_taught',
		null=True,
		blank=True,
	)
	weekly_sessions = models.PositiveIntegerField(default=3)

	class Meta:
		ordering = ['code']

	def __str__(self) -> str:
		return f"{self.name} ({self.code})"
