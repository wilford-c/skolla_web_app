from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from auditlog.services import log_event
from students.models import Student

from .forms import AssessmentForm, BulkGradeForm, ClassroomForm, GradeForm, SubjectForm
from .models import Assessment, Classroom, Grade, Subject

User = get_user_model()


@login_required
def classroom_list(request):
	classrooms = Classroom.objects.select_related('homeroom_teacher').prefetch_related('subjects')
	can_manage = request.user.is_superuser or request.user.role == User.Role.ADMIN
	can_create = can_manage or request.user.role == User.Role.STAFF
	return render(
		request,
		'academics/classroom_list.html',
		{
			'classrooms': classrooms,
			'can_manage_classrooms': can_manage,
			'can_create_classrooms': can_create,
		},
	)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF)
def classroom_create(request):
	form = ClassroomForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		classroom = form.save()
		log_event(
			request=request,
			action='classroom.create',
			entity_type='Classroom',
			entity_id=str(classroom.pk),
			description=f'Created classroom {classroom.code}.',
		)
		messages.success(request, 'Classroom created successfully.')
		return redirect('academics:classrooms')
	return render(
		request,
		'academics/classroom_form.html',
		{
			'form': form,
			'window_title': 'New Class · Skola',
			'page_title': 'Create Classroom',
			'page_label': 'Academics',
			'submit_label': 'Save Classroom',
		},
	)


@login_required
@role_required(User.Role.ADMIN)
def classroom_update(request, pk):
	classroom = get_object_or_404(Classroom, pk=pk)
	form = ClassroomForm(request.POST or None, instance=classroom)
	if request.method == 'POST' and form.is_valid():
		classroom = form.save()
		log_event(
			request=request,
			action='classroom.update',
			entity_type='Classroom',
			entity_id=str(classroom.pk),
			description=f'Updated classroom {classroom.code}.',
		)
		messages.success(request, 'Classroom updated successfully.')
		return redirect('academics:classrooms')
	return render(
		request,
		'academics/classroom_form.html',
		{
			'form': form,
			'window_title': 'Edit Class · Skola',
			'page_title': 'Edit Classroom',
			'page_label': 'Academics',
			'submit_label': 'Update Classroom',
		},
	)


@login_required
@role_required(User.Role.ADMIN)
@require_POST
def classroom_delete(request, pk):
	classroom = get_object_or_404(Classroom, pk=pk)
	classroom_id = str(classroom.pk)
	classroom_code = classroom.code
	classroom.delete()
	log_event(
		request=request,
		action='classroom.delete',
		entity_type='Classroom',
		entity_id=classroom_id,
		description=f'Deleted classroom {classroom_code}.',
		severity='WARNING',
	)
	messages.success(request, 'Classroom deleted successfully.')
	return redirect('academics:classrooms')


@login_required
def subject_list(request):
	subjects = Subject.objects.select_related('classroom', 'teacher')
	can_manage = request.user.is_superuser or request.user.role == User.Role.ADMIN
	can_create = can_manage or request.user.role in {User.Role.STAFF, User.Role.TEACHER}
	return render(
		request,
		'academics/subject_list.html',
		{
			'subjects': subjects,
			'can_manage_subjects': can_manage,
			'can_create_subjects': can_create,
		},
	)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def subject_create(request):
	form = SubjectForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		subject = form.save()
		log_event(
			request=request,
			action='subject.create',
			entity_type='Subject',
			entity_id=str(subject.pk),
			description=f'Created subject {subject.code}.',
		)
		messages.success(request, 'Subject created successfully.')
		return redirect('academics:subjects')
	return render(
		request,
		'academics/subject_form.html',
		{
			'form': form,
			'window_title': 'New Subject · Skola',
			'page_title': 'Create Subject',
			'page_label': 'Curriculum',
			'submit_label': 'Save Subject',
		},
	)


@login_required
@role_required(User.Role.ADMIN)
def subject_update(request, pk):
	subject = get_object_or_404(Subject, pk=pk)
	form = SubjectForm(request.POST or None, instance=subject)
	if request.method == 'POST' and form.is_valid():
		subject = form.save()
		log_event(
			request=request,
			action='subject.update',
			entity_type='Subject',
			entity_id=str(subject.pk),
			description=f'Updated subject {subject.code}.',
		)
		messages.success(request, 'Subject updated successfully.')
		return redirect('academics:subjects')
	return render(
		request,
		'academics/subject_form.html',
		{
			'form': form,
			'window_title': 'Edit Subject · Skola',
			'page_title': 'Edit Subject',
			'page_label': 'Curriculum',
			'submit_label': 'Update Subject',
		},
	)


@login_required
@role_required(User.Role.ADMIN)
@require_POST
def subject_delete(request, pk):
	subject = get_object_or_404(Subject, pk=pk)
	subject_id = str(subject.pk)
	subject_code = subject.code
	subject.delete()
	log_event(
		request=request,
		action='subject.delete',
		entity_type='Subject',
		entity_id=subject_id,
		description=f'Deleted subject {subject_code}.',
		severity='WARNING',
	)
	messages.success(request, 'Subject deleted successfully.')
	return redirect('academics:subjects')


# ============ Assessment Views ============

@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def assessment_list(request):
	assessments = Assessment.objects.select_related('subject', 'subject__classroom', 'created_by')
	
	# Filter by subject if provided
	subject_id = request.GET.get('subject')
	if subject_id:
		assessments = assessments.filter(subject_id=subject_id)
	
	# Filter by type if provided
	assessment_type = request.GET.get('type')
	if assessment_type:
		assessments = assessments.filter(assessment_type=assessment_type)
	
	can_manage = request.user.is_superuser or request.user.role == User.Role.ADMIN
	can_create = can_manage or request.user.role in {User.Role.STAFF, User.Role.TEACHER}
	
	return render(
		request,
		'academics/assessment_list.html',
		{
			'assessments': assessments,
			'subjects': Subject.objects.all(),
			'assessment_types': Assessment.Type.choices,
			'selected_subject': subject_id,
			'selected_type': assessment_type,
			'can_manage_assessments': can_manage,
			'can_create_assessments': can_create,
		},
	)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def assessment_create(request):
	form = AssessmentForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		assessment = form.save(commit=False)
		assessment.created_by = request.user
		assessment.save()
		log_event(
			request=request,
			action='assessment.create',
			entity_type='Assessment',
			entity_id=str(assessment.pk),
			description=f'Created assessment "{assessment.name}".',
		)
		messages.success(request, 'Assessment created successfully.')
		return redirect('academics:assessments')
	return render(
		request,
		'academics/assessment_form.html',
		{
			'form': form,
			'window_title': 'New Assessment · Skola',
			'page_title': 'Create Assessment',
			'page_label': 'Grading',
			'submit_label': 'Save Assessment',
		},
	)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def assessment_update(request, pk):
	assessment = get_object_or_404(Assessment, pk=pk)
	form = AssessmentForm(request.POST or None, instance=assessment)
	if request.method == 'POST' and form.is_valid():
		assessment = form.save()
		log_event(
			request=request,
			action='assessment.update',
			entity_type='Assessment',
			entity_id=str(assessment.pk),
			description=f'Updated assessment "{assessment.name}".',
		)
		messages.success(request, 'Assessment updated successfully.')
		return redirect('academics:assessments')
	return render(
		request,
		'academics/assessment_form.html',
		{
			'form': form,
			'window_title': 'Edit Assessment · Skola',
			'page_title': 'Edit Assessment',
			'page_label': 'Grading',
			'submit_label': 'Update Assessment',
		},
	)


@login_required
@role_required(User.Role.ADMIN)
@require_POST
def assessment_delete(request, pk):
	assessment = get_object_or_404(Assessment, pk=pk)
	assessment_id = str(assessment.pk)
	assessment_name = assessment.name
	assessment.delete()
	log_event(
		request=request,
		action='assessment.delete',
		entity_type='Assessment',
		entity_id=assessment_id,
		description=f'Deleted assessment "{assessment_name}".',
		severity='WARNING',
	)
	messages.success(request, 'Assessment deleted successfully.')
	return redirect('academics:assessments')


# ============ Grade Views ============

@login_required
def grade_list(request):
	"""List all grades with filtering options."""
	user = request.user
	
	# Base queryset
	grades = Grade.objects.select_related(
		'student',
		'assessment',
		'assessment__subject',
		'assessment__subject__classroom',
		'entered_by',
	)
	
	# Role-based filtering
	if user.role == User.Role.STUDENT:
		# Students can only see their own grades
		student_profile = getattr(user, 'student_profile', None)
		if student_profile:
			grades = grades.filter(student=student_profile)
		else:
			grades = grades.none()
	elif user.role == User.Role.TEACHER:
		# Teachers can see grades for subjects they teach
		grades = grades.filter(assessment__subject__teacher=user)
	# Admin and Staff can see all grades
	
	# Apply filters
	subject_id = request.GET.get('subject')
	if subject_id:
		grades = grades.filter(assessment__subject_id=subject_id)
	
	student_id = request.GET.get('student')
	if student_id:
		grades = grades.filter(student_id=student_id)
	
	assessment_id = request.GET.get('assessment')
	if assessment_id:
		grades = grades.filter(assessment_id=assessment_id)
	
	can_manage = user.is_superuser or user.role == User.Role.ADMIN
	can_enter = can_manage or user.role in {User.Role.STAFF, User.Role.TEACHER}
	
	return render(
		request,
		'academics/grade_list.html',
		{
			'grades': grades,
			'subjects': Subject.objects.all(),
			'students': Student.objects.filter(status=Student.Status.ACTIVE),
			'assessments': Assessment.objects.all().select_related('subject'),
			'selected_subject': subject_id,
			'selected_student': student_id,
			'selected_assessment': assessment_id,
			'can_manage_grades': can_manage,
			'can_enter_grades': can_enter,
		},
	)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def grade_create(request):
	"""Create a single grade entry."""
	form = GradeForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		grade = form.save(commit=False)
		grade.entered_by = request.user
		grade.save()
		log_event(
			request=request,
			action='grade.create',
			entity_type='Grade',
			entity_id=str(grade.pk),
			description=f'Recorded grade for {grade.student.admission_number}.',
		)
		messages.success(request, 'Grade recorded successfully.')
		return redirect('academics:grades')
	return render(
		request,
		'academics/grade_form.html',
		{
			'form': form,
			'window_title': 'Enter Grade · Skola',
			'page_title': 'Record Grade',
			'page_label': 'Grading',
			'submit_label': 'Save Grade',
		},
	)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def grade_bulk_entry(request):
	"""Bulk grade entry for all students in an assessment."""
	form = BulkGradeForm(request.POST or None)
	assessment = None
	students = []
	
	if request.method == 'POST':
		if 'select_assessment' in request.POST and form.is_valid():
			assessment = form.cleaned_data['assessment']
			# Get all students in the subject's classroom
			students = Student.objects.filter(
				status=Student.Status.ACTIVE
			).order_by('admission_number')
			
			# Get existing grades for this assessment
			existing_grades = {
				grade.student_id: grade
				for grade in Grade.objects.filter(assessment=assessment).select_related('student')
			}
			
			# Prepare student data with existing grades
			students_data = []
			for student in students:
				existing_grade = existing_grades.get(student.id)
				students_data.append({
					'student': student,
					'existing_score': existing_grade.score if existing_grade else None,
					'existing_remarks': existing_grade.remarks if existing_grade else '',
				})
			
			return render(
				request,
				'academics/grade_bulk_entry.html',
				{
					'form': form,
					'assessment': assessment,
					'students_data': students_data,
					'show_entry_form': True,
				},
			)
		
		elif 'save_grades' in request.POST:
			assessment_id = request.POST.get('assessment_id')
			assessment = get_object_or_404(Assessment, pk=assessment_id)
			
			# Process bulk grades
			with transaction.atomic():
				count_updated = 0
				count_created = 0
				
				for key, value in request.POST.items():
					if key.startswith('score_'):
						student_id = key.split('_')[1]
						score = value.strip()
						
						if not score:
							continue
						
						remarks = request.POST.get(f'remarks_{student_id}', '')
						
						try:
							student = Student.objects.get(pk=student_id)
							grade, created = Grade.objects.update_or_create(
								student=student,
								assessment=assessment,
								defaults={
									'score': score,
									'remarks': remarks,
									'entered_by': request.user,
								},
							)
							if created:
								count_created += 1
							else:
								count_updated += 1
						except (Student.DoesNotExist, ValueError):
							continue
				
				messages.success(
					request,
					f'Grades saved: {count_created} created, {count_updated} updated.',
				)
				return redirect('academics:grades')
	
	return render(
		request,
		'academics/grade_bulk_entry.html',
		{
			'form': form,
			'show_entry_form': False,
		},
	)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def grade_update(request, pk):
	"""Update an existing grade."""
	grade = get_object_or_404(Grade, pk=pk)
	form = GradeForm(request.POST or None, instance=grade)
	if request.method == 'POST' and form.is_valid():
		grade = form.save()
		log_event(
			request=request,
			action='grade.update',
			entity_type='Grade',
			entity_id=str(grade.pk),
			description=f'Updated grade for {grade.student.admission_number}.',
		)
		messages.success(request, 'Grade updated successfully.')
		return redirect('academics:grades')
	return render(
		request,
		'academics/grade_form.html',
		{
			'form': form,
			'window_title': 'Edit Grade · Skola',
			'page_title': 'Update Grade',
			'page_label': 'Grading',
			'submit_label': 'Update Grade',
		},
	)


@login_required
@role_required(User.Role.ADMIN)
@require_POST
def grade_delete(request, pk):
	grade = get_object_or_404(Grade, pk=pk)
	grade_id = str(grade.pk)
	student_label = grade.student.admission_number
	grade.delete()
	log_event(
		request=request,
		action='grade.delete',
		entity_type='Grade',
		entity_id=grade_id,
		description=f'Deleted grade for {student_label}.',
		severity='WARNING',
	)
	messages.success(request, 'Grade deleted successfully.')
	return redirect('academics:grades')


@login_required
def student_grades(request, student_id=None):
	"""View grades for a specific student with calculations."""
	user = request.user
	
	# Determine which student's grades to show
	if student_id:
		# Admin/Staff/Teacher/Guardian viewing specific student
		if user.role in {User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER}:
			student = get_object_or_404(Student, pk=student_id)
		elif user.role == User.Role.GUARDIAN:
			# Guardians can only view their linked children's grades
			student = get_object_or_404(Student, pk=student_id, guardian_user=user)
		else:
			messages.error(request, 'You do not have permission to view this page.')
			return redirect('accounts:dashboard')
	else:
		# Student viewing their own grades
		if user.role == User.Role.STUDENT:
			student = getattr(user, 'student_profile', None)
			if not student:
				messages.error(request, 'No student profile linked to your account.')
				return redirect('accounts:dashboard')
		else:
			messages.error(request, 'Please select a student.')
			return redirect('academics:grades')
	
	# Get all grades for this student
	grades = Grade.objects.filter(student=student).select_related(
		'assessment',
		'assessment__subject',
		'assessment__subject__classroom',
	).order_by('-assessment__date')
	
	# Group grades by subject
	grades_by_subject = {}
	for grade in grades:
		subject = grade.assessment.subject
		if subject not in grades_by_subject:
			grades_by_subject[subject] = []
		grades_by_subject[subject].append(grade)
	
	# Calculate subject averages
	subject_stats = []
	for subject, subject_grades in grades_by_subject.items():
		total_weighted_score = 0
		total_weight = 0
		
		for grade in subject_grades:
			percentage = grade.percentage
			weight = float(grade.assessment.weight)
			total_weighted_score += (percentage * weight)
			total_weight += weight
		
		if total_weight > 0:
			weighted_average = total_weighted_score / total_weight
		else:
			weighted_average = 0
		
		# Determine letter grade
		if weighted_average >= 90:
			letter = 'A'
		elif weighted_average >= 80:
			letter = 'B'
		elif weighted_average >= 70:
			letter = 'C'
		elif weighted_average >= 60:
			letter = 'D'
		else:
			letter = 'F'
		
		subject_stats.append({
			'subject': subject,
			'grades': subject_grades,
			'weighted_average': round(weighted_average, 2),
			'letter_grade': letter,
			'grade_count': len(subject_grades),
		})
	
	# Calculate overall GPA (simple average of subject averages)
	if subject_stats:
		overall_average = sum(s['weighted_average'] for s in subject_stats) / len(subject_stats)
	else:
		overall_average = 0
	
	return render(
		request,
		'academics/student_grades.html',
		{
			'student': student,
			'subject_stats': subject_stats,
			'overall_average': round(overall_average, 2),
			'total_grades': grades.count(),
		},
	)
