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

	class Meta:
		ordering = ['-date', 'student__admission_number']
		unique_together = ('student', 'subject', 'date')

	def __str__(self) -> str:
		return f"{self.student.full_name} - {self.date} ({self.get_status_display()})"
