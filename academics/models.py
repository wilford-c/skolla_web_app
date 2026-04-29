from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Sum

from students.models import Student


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


class Assessment(models.Model):
	"""Assessment type/category for grading (e.g., Quiz, Exam, Project)."""
	
	class Type(models.TextChoices):
		QUIZ = 'QUIZ', 'Quiz'
		TEST = 'TEST', 'Test'
		EXAM = 'EXAM', 'Exam'
		ASSIGNMENT = 'ASSIGNMENT', 'Assignment'
		PROJECT = 'PROJECT', 'Project'
		PARTICIPATION = 'PARTICIPATION', 'Participation'
		HOMEWORK = 'HOMEWORK', 'Homework'
	
	name = models.CharField(max_length=120)
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assessments')
	assessment_type = models.CharField(max_length=20, choices=Type.choices, default=Type.QUIZ)
	max_score = models.DecimalField(
		max_digits=6,
		decimal_places=2,
		default=100.00,
		validators=[MinValueValidator(0)],
		help_text='Maximum possible score for this assessment',
	)
	weight = models.DecimalField(
		max_digits=5,
		decimal_places=2,
		default=1.00,
		validators=[MinValueValidator(0), MaxValueValidator(100)],
		help_text='Weight/percentage of this assessment towards final grade',
	)
	date = models.DateField()
	description = models.TextField(blank=True)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		related_name='assessments_created',
	)
	created_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering = ['-date', 'name']
	
	def __str__(self) -> str:
		return f"{self.name} - {self.subject.name} ({self.get_assessment_type_display()})"


class Grade(models.Model):
	"""Individual student grade for an assessment."""
	
	student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
	assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='grades')
	score = models.DecimalField(
		max_digits=6,
		decimal_places=2,
		validators=[MinValueValidator(0)],
		help_text='Score achieved by the student',
	)
	remarks = models.TextField(blank=True, help_text='Teacher comments or notes')
	entered_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		related_name='grades_entered',
	)
	entered_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['-assessment__date', 'student__admission_number']
		unique_together = ('student', 'assessment')
	
	def __str__(self) -> str:
		return f"{self.student.full_name} - {self.assessment.name}: {self.score}/{self.assessment.max_score}"
	
	@property
	def percentage(self) -> float:
		"""Calculate percentage score."""
		if self.assessment.max_score > 0:
			return (float(self.score) / float(self.assessment.max_score)) * 100
		return 0.0
	
	@property
	def letter_grade(self) -> str:
		"""Convert percentage to letter grade."""
		pct = self.percentage
		if pct >= 90:
			return 'A'
		elif pct >= 80:
			return 'B'
		elif pct >= 70:
			return 'C'
		elif pct >= 60:
			return 'D'
		else:
			return 'F'
	
	def clean(self):
		"""Validate that score doesn't exceed max_score."""
		from django.core.exceptions import ValidationError
		if self.score and self.assessment and self.score > self.assessment.max_score:
			raise ValidationError(
				f'Score ({self.score}) cannot exceed maximum score ({self.assessment.max_score})'
			)
