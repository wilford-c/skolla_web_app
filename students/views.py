import csv
from datetime import datetime
from io import TextIOWrapper

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from academics.models import Classroom
from auditlog.services import log_event

from .forms import CSVImportForm, StudentForm, StudentTransferForm
from .models import Student

User = get_user_model()


@login_required
def student_list(request):
	students = Student.objects.select_related('user', 'guardian_user', 'current_classroom').all()
	can_manage = request.user.is_superuser or request.user.role == User.Role.ADMIN
	can_create = can_manage or request.user.role == User.Role.STAFF
	can_view_enrollments = can_create
	return render(
		request,
		'students/student_list.html',
		{
			'students': students,
			'can_manage_students': can_manage,
			'can_create_students': can_create,
			'can_view_enrollments': can_view_enrollments,
		},
	)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF)
def student_create(request):
	form = StudentForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		student = form.save(commit=False)
		student.save(
			enrollment_actor=request.user,
			enrollment_note='Student onboarded via enrollment form.',
		)
		log_event(
			request=request,
			action='student.create',
			entity_type='Student',
			entity_id=str(student.pk),
			description=f'Created student {student.admission_number} ({student.full_name}).',
		)
		messages.success(request, 'Student profile created successfully.')
		return redirect('students:list')

	return render(
		request,
		'students/student_form.html',
		{
			'form': form,
			'window_title': 'New Student · Skola',
			'page_title': 'Add New Student',
			'page_label': 'Enrollment',
			'submit_label': 'Save Student',
		},
	)


@login_required
@role_required(User.Role.ADMIN)
def student_update(request, pk):
	student = get_object_or_404(
		Student.objects.select_related('current_classroom'),
		pk=pk,
	)
	previous_classroom = student.current_classroom
	previous_status = student.status
	form = StudentForm(request.POST or None, instance=student)
	if request.method == 'POST' and form.is_valid():
		student = form.save(commit=False)
		note_parts = []

		if previous_classroom != student.current_classroom:
			if previous_classroom and student.current_classroom:
				note_parts.append(
					f'Transferred from {previous_classroom.code} to {student.current_classroom.code}.'
				)
			elif student.current_classroom:
				note_parts.append(f'Assigned to classroom {student.current_classroom.code}.')
			else:
				note_parts.append('Classroom assignment removed.')

		if previous_status != student.status:
			old_status = dict(Student.Status.choices).get(previous_status, previous_status)
			new_status = student.get_status_display()
			note_parts.append(f'Status updated from {old_status} to {new_status}.')

		student.save(
			enrollment_actor=request.user,
			enrollment_note=' '.join(note_parts) or 'Student profile updated.',
		)
		log_event(
			request=request,
			action='student.update',
			entity_type='Student',
			entity_id=str(student.pk),
			description=f'Updated student {student.admission_number} ({student.full_name}).',
			metadata={
				'previous_classroom': previous_classroom.code if previous_classroom else '',
				'new_classroom': student.current_classroom.code if student.current_classroom else '',
				'previous_status': previous_status,
				'new_status': student.status,
			},
		)
		messages.success(request, 'Student profile updated successfully.')
		return redirect('students:list')

	return render(
		request,
		'students/student_form.html',
		{
			'form': form,
			'window_title': 'Edit Student · Skola',
			'page_title': 'Edit Student',
			'page_label': 'Enrollment',
			'submit_label': 'Update Student',
		},
	)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF)
def student_enrollments(request, pk):
	student = get_object_or_404(Student.objects.select_related('current_classroom'), pk=pk)
	enrollments = student.enrollments.select_related('classroom', 'onboarded_by').all()
	can_transfer = request.user.is_superuser or request.user.role == User.Role.ADMIN
	transfer_form = StudentTransferForm(student=student)

	return render(
		request,
		'students/student_enrollments.html',
		{
			'student': student,
			'enrollments': enrollments,
			'can_transfer': can_transfer,
			'transfer_form': transfer_form,
		},
	)


@login_required
@role_required(User.Role.ADMIN)
@require_POST
def student_transfer(request, pk):
	student = get_object_or_404(Student.objects.select_related('current_classroom'), pk=pk)
	form = StudentTransferForm(request.POST, student=student)

	if not form.is_valid():
		for field_name, field_errors in form.errors.items():
			field_label = form.fields.get(field_name).label if field_name in form.fields else field_name
			for error in field_errors:
				messages.error(request, f'{field_label}: {error}')
		return redirect('students:enrollments', pk=student.pk)

	new_classroom = form.cleaned_data['new_classroom']
	effective_date = form.cleaned_data['effective_date']
	note = form.cleaned_data['note'].strip()
	previous_classroom = student.current_classroom

	if previous_classroom and previous_classroom.pk == new_classroom.pk:
		messages.error(request, 'Student is already enrolled in the selected classroom.')
		return redirect('students:enrollments', pk=student.pk)

	transfer_note = (
		f'Transferred from {previous_classroom.code} to {new_classroom.code}.'
		if previous_classroom
		else f'Onboarded into classroom {new_classroom.code}.'
	)
	if note:
		transfer_note = f'{transfer_note} {note}'

	with transaction.atomic():
		student.current_classroom = new_classroom
		student.status = Student.Status.ACTIVE
		student.save(
			enrollment_actor=request.user,
			enrollment_note=transfer_note,
			enrollment_effective_date=effective_date,
		)

	log_event(
		request=request,
		action='student.transfer',
		entity_type='Student',
		entity_id=str(student.pk),
		description=f'Transferred {student.admission_number} to {new_classroom.code}.',
		metadata={
			'from_classroom': previous_classroom.code if previous_classroom else '',
			'to_classroom': new_classroom.code,
			'effective_date': effective_date.isoformat(),
		},
	)

	messages.success(request, f'{student.full_name} transferred successfully.')
	return redirect('students:enrollments', pk=student.pk)


@login_required
@role_required(User.Role.ADMIN)
@require_POST
def student_delete(request, pk):
	student = get_object_or_404(Student, pk=pk)
	student_id = str(student.pk)
	student_label = student.admission_number
	student.delete()
	log_event(
		request=request,
		action='student.delete',
		entity_type='Student',
		entity_id=student_id,
		description=f'Deleted student {student_label}.',
		severity='WARNING',
	)
	
	# Handle HTMX requests
	if request.headers.get('HX-Request'):
		# Return empty content (row will be swapped out)
		return HttpResponse('')
	
	messages.success(request, 'Student profile deleted successfully.')
	return redirect('students:list')


@login_required
@role_required(User.Role.ADMIN)
def student_import(request):
	# Handle confirm action (import from session data)
	if request.method == 'POST' and 'confirm' in request.POST:
		valid_students = request.session.get('import_preview_data', [])
		
		if not valid_students:
			messages.error(request, 'No import data found. Please upload the CSV file again.')
			return redirect('students:import')
		
		try:
			# Import students
			with transaction.atomic():
				for data in valid_students:
					# Convert date string back to date object
					if isinstance(data['date_of_birth'], str):
						data['date_of_birth'] = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
					student = Student(**data)
					student.save(
						enrollment_actor=request.user,
						enrollment_note='Student onboarded via CSV import.',
					)

			log_event(
				request=request,
				action='student.import.csv',
				entity_type='Student',
				entity_id='batch',
				description=f'Imported {len(valid_students)} students via CSV.',
			)
			
			# Clear session data
			request.session.pop('import_preview_data', None)
			
			messages.success(
				request,
				f'Successfully imported {len(valid_students)} student(s).',
			)
			return redirect('students:list')
			
		except Exception as e:
			messages.error(request, f'Error during import: {str(e)}')
			return redirect('students:import')
	
	# Handle cancel action
	if request.method == 'POST' and 'cancel' in request.POST:
		request.session.pop('import_preview_data', None)
		return redirect('students:import')
	
	# Handle CSV upload and preview
	if request.method == 'POST' and 'preview' in request.POST:
		form = CSVImportForm(request.POST, request.FILES)
		if form.is_valid():
			csv_file = request.FILES['csv_file']
			
			# Parse CSV file
			try:
				# Decode the uploaded file
				file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
				csv_reader = csv.DictReader(file_data)
				
				# Validate required columns
				required_columns = {'admission_number', 'first_name', 'last_name', 'date_of_birth', 'guardian_name'}
				csv_columns = set(csv_reader.fieldnames or [])
				
				if not required_columns.issubset(csv_columns):
					missing = required_columns - csv_columns
					messages.error(
						request,
						f'CSV is missing required columns: {", ".join(missing)}',
					)
					return render(request, 'students/student_import.html', {'form': form})
				
				# Process rows and validate
				rows = list(csv_reader)
				errors = []
				valid_students = []
				
				for idx, row in enumerate(rows, start=2):  # Start at 2 (row 1 is header)
					try:
						# Validate admission number uniqueness
						admission_number = row['admission_number'].strip()
						if not admission_number:
							errors.append(f'Row {idx}: admission_number is required')
							continue
						
						if Student.objects.filter(admission_number=admission_number).exists():
							errors.append(f'Row {idx}: admission_number "{admission_number}" already exists')
							continue
						
						# Parse date
						try:
							date_of_birth = datetime.strptime(row['date_of_birth'].strip(), '%Y-%m-%d').date()
						except ValueError:
							errors.append(f'Row {idx}: Invalid date format for date_of_birth (use YYYY-MM-DD)')
							continue

						# Resolve optional classroom by code
						classroom_code = row.get('current_classroom_code', '').strip()
						current_classroom_id = None
						if classroom_code:
							classroom = Classroom.objects.filter(code__iexact=classroom_code).first()
							if not classroom:
								errors.append(f'Row {idx}: Unknown current_classroom_code "{classroom_code}"')
								continue
							current_classroom_id = classroom.id
						
						# Prepare student data
						student_data = {
							'admission_number': admission_number,
							'first_name': row['first_name'].strip(),
							'last_name': row['last_name'].strip(),
							'date_of_birth': date_of_birth.strftime('%Y-%m-%d'),  # Store as string for session
							'current_classroom_id': current_classroom_id,
							'guardian_name': row['guardian_name'].strip(),
							'contact_email': row.get('contact_email', '').strip(),
							'contact_phone': row.get('contact_phone', '').strip(),
							'status': row.get('status', 'ACTIVE').strip().upper(),
						}
						
						# Validate status
						if student_data['status'] not in dict(Student.Status.choices):
							student_data['status'] = Student.Status.ACTIVE
						
						valid_students.append(student_data)
						
					except Exception as e:
						errors.append(f'Row {idx}: {str(e)}')
				
				# Store valid students in session for confirmation
				if valid_students and not errors:
					request.session['import_preview_data'] = valid_students
				
				# Show preview
				return render(
					request,
					'students/student_import.html',
					{
						'form': form,
						'preview': True,
						'valid_students': valid_students,
						'errors': errors,
						'total_rows': len(rows),
					},
				)
				
			except Exception as e:
				messages.error(request, f'Error processing CSV file: {str(e)}')
				return render(request, 'students/student_import.html', {'form': form})
	
	# GET request or initial form
	form = CSVImportForm()
	return render(request, 'students/student_import.html', {'form': form})


@login_required
@role_required(User.Role.ADMIN)
def student_export(request):
	# Get filter parameters
	status_filter = request.GET.get('status', '')
	
	# Build queryset
	students = Student.objects.all()
	if status_filter and status_filter in dict(Student.Status.choices):
		students = students.filter(status=status_filter)
	
	# Create CSV response
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="students_export.csv"'
	
	writer = csv.writer(response)
	
	# Write header
	writer.writerow([
		'admission_number',
		'first_name',
		'last_name',
		'date_of_birth',
		'current_classroom_code',
		'guardian_name',
		'contact_email',
		'contact_phone',
		'status',
		'enrolled_on',
	])
	
	# Write data rows
	for student in students:
		writer.writerow([
			student.admission_number,
			student.first_name,
			student.last_name,
			student.date_of_birth.strftime('%Y-%m-%d'),
			student.current_classroom.code if student.current_classroom else '',
			student.guardian_name,
			student.contact_email,
			student.contact_phone,
			student.status,
			student.enrolled_on.strftime('%Y-%m-%d'),
		])
	
	return response


@login_required
def student_search(request):
	"""HTMX endpoint for live student search."""
	query = request.GET.get('search', '').strip()
	
	students = Student.objects.select_related('user', 'guardian_user', 'current_classroom').all()
	
	if query:
		from django.db.models import Q
		students = students.filter(
			Q(admission_number__icontains=query) |
			Q(first_name__icontains=query) |
			Q(last_name__icontains=query) |
			Q(guardian_name__icontains=query) |
			Q(contact_email__icontains=query) |
			Q(contact_phone__icontains=query)
		)
	
	can_manage = request.user.is_superuser or request.user.role == User.Role.ADMIN
	can_view_enrollments = can_manage or request.user.role == User.Role.STAFF
	
	return render(
		request,
		'students/partials/student_rows.html',
		{
			'students': students,
			'can_manage_students': can_manage,
			'can_view_enrollments': can_view_enrollments,
		},
	)
