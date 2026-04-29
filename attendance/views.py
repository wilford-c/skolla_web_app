import csv
from datetime import datetime, timedelta
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from academics.models import Classroom, Subject
from auditlog.services import log_event
from students.models import Student

from .forms import AttendanceForm, NotificationPreferenceForm, ReportBuilderForm, ReportTemplateForm
from .models import AttendanceRecord, NotificationPreference, ReportTemplate
from .utils import ReportGenerator

User = get_user_model()


@login_required
def attendance_list(request):
	records = AttendanceRecord.objects.select_related('student', 'classroom', 'subject')
	status_filter = request.GET.get('status')
	if status_filter:
		records = records.filter(status=status_filter)
	can_manage = request.user.is_superuser or request.user.role == User.Role.ADMIN
	can_record = can_manage or request.user.role in {User.Role.STAFF, User.Role.TEACHER}
	return render(
		request,
		'attendance/attendance_list.html',
		{
			'records': records,
			'status_filter': status_filter,
			'statuses': AttendanceRecord.Status.choices,
			'can_manage_attendance': can_manage,
			'can_record_attendance': can_record,
		},
	)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def attendance_mark(request):
	form = AttendanceForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		record = form.save(commit=False)
		record.recorded_by = request.user
		record.save()
		log_event(
			request=request,
			action='attendance.create',
			entity_type='AttendanceRecord',
			entity_id=str(record.pk),
			description=f'Recorded attendance for {record.student.admission_number} on {record.date}.',
			metadata={'status': record.status},
		)
		messages.success(request, 'Attendance recorded successfully.')
		return redirect('attendance:list')

	return render(
		request,
		'attendance/attendance_form.html',
		{
			'form': form,
			'window_title': 'Record Attendance · Skola',
			'page_title': 'Record Attendance',
			'page_label': 'Daily Operations',
			'submit_label': 'Submit Attendance',
		},
	)


@login_required
@role_required(User.Role.ADMIN)
def attendance_update(request, pk):
	record = get_object_or_404(AttendanceRecord, pk=pk)
	form = AttendanceForm(request.POST or None, instance=record)
	if request.method == 'POST' and form.is_valid():
		updated = form.save()
		log_event(
			request=request,
			action='attendance.update',
			entity_type='AttendanceRecord',
			entity_id=str(updated.pk),
			description=f'Updated attendance for {updated.student.admission_number} on {updated.date}.',
			metadata={'status': updated.status},
		)
		messages.success(request, 'Attendance record updated successfully.')
		return redirect('attendance:list')
	return render(
		request,
		'attendance/attendance_form.html',
		{
			'form': form,
			'window_title': 'Edit Attendance · Skola',
			'page_title': 'Edit Attendance Record',
			'page_label': 'Daily Operations',
			'submit_label': 'Update Attendance',
		},
	)


@login_required
@role_required(User.Role.ADMIN)
@require_POST
def attendance_delete(request, pk):
	record = get_object_or_404(AttendanceRecord, pk=pk)
	record_id = str(record.pk)
	student_label = record.student.admission_number
	record_date = record.date.isoformat()
	record.delete()
	log_event(
		request=request,
		action='attendance.delete',
		entity_type='AttendanceRecord',
		entity_id=record_id,
		description=f'Deleted attendance for {student_label} on {record_date}.',
		severity='WARNING',
	)
	messages.success(request, 'Attendance record deleted successfully.')
	return redirect('attendance:list')


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def attendance_reports(request):
	"""
	Generate attendance reports with filtering and statistics.
	"""
	# Get filter parameters
	date_from = request.GET.get('date_from', '')
	date_to = request.GET.get('date_to', '')
	classroom_id = request.GET.get('classroom', '')
	subject_id = request.GET.get('subject', '')
	student_id = request.GET.get('student', '')
	status = request.GET.get('status', '')
	
	# Default date range: last 30 days
	if not date_from:
		date_from = (timezone.now().date() - timedelta(days=30)).strftime('%Y-%m-%d')
	if not date_to:
		date_to = timezone.now().date().strftime('%Y-%m-%d')
	
	# Build queryset
	records = AttendanceRecord.objects.select_related(
		'student', 'classroom', 'subject', 'recorded_by'
	)
	
	# Apply filters
	if date_from:
		records = records.filter(date__gte=date_from)
	if date_to:
		records = records.filter(date__lte=date_to)
	if classroom_id:
		records = records.filter(classroom_id=classroom_id)
	if subject_id:
		records = records.filter(subject_id=subject_id)
	if student_id:
		records = records.filter(student_id=student_id)
	if status:
		records = records.filter(status=status)
	
	# Calculate statistics
	total_records = records.count()
	status_counts = records.values('status').annotate(count=Count('id'))
	status_stats = {item['status']: item['count'] for item in status_counts}
	
	# Student-level statistics (students with most absences)
	absent_students = (
		records.filter(status__in=[AttendanceRecord.Status.ABSENT, AttendanceRecord.Status.LATE])
		.values('student__id', 'student__admission_number', 'student__first_name', 'student__last_name')
		.annotate(absence_count=Count('id'))
		.order_by('-absence_count')[:10]
	)
	
	# Daily trends (for chart)
	daily_stats = (
		records.values('date')
		.annotate(
			total=Count('id'),
			present=Count('id', filter=Q(status=AttendanceRecord.Status.PRESENT)),
			absent=Count('id', filter=Q(status=AttendanceRecord.Status.ABSENT)),
			late=Count('id', filter=Q(status=AttendanceRecord.Status.LATE)),
			excused=Count('id', filter=Q(status=AttendanceRecord.Status.EXCUSED)),
		)
		.order_by('date')
	)
	
	# Prepare chart data
	chart_labels = [str(item['date']) for item in daily_stats]
	chart_data = {
		'present': [item['present'] for item in daily_stats],
		'absent': [item['absent'] for item in daily_stats],
		'late': [item['late'] for item in daily_stats],
		'excused': [item['excused'] for item in daily_stats],
	}
	
	# Calculate percentages
	present_count = status_stats.get(AttendanceRecord.Status.PRESENT, 0)
	absent_count = status_stats.get(AttendanceRecord.Status.ABSENT, 0)
	late_count = status_stats.get(AttendanceRecord.Status.LATE, 0)
	excused_count = status_stats.get(AttendanceRecord.Status.EXCUSED, 0)
	
	present_pct = (present_count / total_records * 100) if total_records > 0 else 0
	absent_pct = (absent_count / total_records * 100) if total_records > 0 else 0
	late_pct = (late_count / total_records * 100) if total_records > 0 else 0
	excused_pct = (excused_count / total_records * 100) if total_records > 0 else 0
	
	context = {
		'records': records[:100],  # Limit display to recent 100
		'total_records': total_records,
		'present_count': present_count,
		'absent_count': absent_count,
		'late_count': late_count,
		'excused_count': excused_count,
		'present_pct': f'{present_pct:.1f}',
		'absent_pct': f'{absent_pct:.1f}',
		'late_pct': f'{late_pct:.1f}',
		'excused_pct': f'{excused_pct:.1f}',
		'absent_students': absent_students,
		'chart_labels': chart_labels,
		'chart_data': chart_data,
		# Filter options
		'classrooms': Classroom.objects.all(),
		'subjects': Subject.objects.all(),
		'students': Student.objects.filter(status=Student.Status.ACTIVE).order_by('admission_number'),
		'statuses': AttendanceRecord.Status.choices,
		# Filter values
		'date_from': date_from,
		'date_to': date_to,
		'selected_classroom': classroom_id,
		'selected_subject': subject_id,
		'selected_student': student_id,
		'selected_status': status,
	}
	
	return render(request, 'attendance/reports.html', context)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def attendance_export_csv(request):
	"""
	Export attendance records to CSV.
	"""
	# Get filter parameters (same as reports)
	date_from = request.GET.get('date_from', '')
	date_to = request.GET.get('date_to', '')
	classroom_id = request.GET.get('classroom', '')
	subject_id = request.GET.get('subject', '')
	student_id = request.GET.get('student', '')
	status = request.GET.get('status', '')
	
	# Build queryset
	records = AttendanceRecord.objects.select_related(
		'student', 'classroom', 'subject', 'recorded_by'
	).order_by('-date', 'student__admission_number')
	
	# Apply filters
	if date_from:
		records = records.filter(date__gte=date_from)
	if date_to:
		records = records.filter(date__lte=date_to)
	if classroom_id:
		records = records.filter(classroom_id=classroom_id)
	if subject_id:
		records = records.filter(subject_id=subject_id)
	if student_id:
		records = records.filter(student_id=student_id)
	if status:
		records = records.filter(status=status)
	
	# Create CSV response
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
	
	writer = csv.writer(response)
	
	# Write header
	writer.writerow([
		'Date',
		'Student_ID',
		'Student_Name',
		'Classroom',
		'Subject',
		'Status',
		'Notes',
		'Recorded_By',
		'Recorded_At',
	])
	
	# Write data rows
	for record in records:
		writer.writerow([
			record.date.strftime('%Y-%m-%d'),
			record.student.admission_number,
			record.student.full_name,
			record.classroom.name,
			record.subject.name if record.subject else 'N/A',
			record.get_status_display(),
			record.notes,
			record.recorded_by.get_full_name() if record.recorded_by else 'N/A',
			record.recorded_at.strftime('%Y-%m-%d %H:%M:%S'),
		])
	
	return response


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def attendance_export_pdf(request):
	"""
	Export attendance summary report to PDF.
	"""
	try:
		from reportlab.lib import colors
		from reportlab.lib.pagesizes import letter, A4
		from reportlab.lib.styles import getSampleStyleSheet
		from reportlab.lib.units import inch
		from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
	except ImportError:
		messages.error(request, 'PDF export requires reportlab. Please install it: pip install reportlab')
		return redirect('attendance:reports')
	
	# Get filter parameters
	date_from = request.GET.get('date_from', '')
	date_to = request.GET.get('date_to', '')
	classroom_id = request.GET.get('classroom', '')
	subject_id = request.GET.get('subject', '')
	status_filter = request.GET.get('status', '')
	
	# Build queryset
	records = AttendanceRecord.objects.select_related('student', 'classroom', 'subject')
	
	if date_from:
		records = records.filter(date__gte=date_from)
	if date_to:
		records = records.filter(date__lte=date_to)
	if classroom_id:
		records = records.filter(classroom_id=classroom_id)
	if subject_id:
		records = records.filter(subject_id=subject_id)
	if status_filter:
		records = records.filter(status=status_filter)
	
	# Calculate statistics
	total_records = records.count()
	status_counts = records.values('status').annotate(count=Count('id'))
	status_stats = {item['status']: item['count'] for item in status_counts}
	
	# Create PDF
	buffer = BytesIO()
	doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
	
	# Container for PDF elements
	elements = []
	styles = getSampleStyleSheet()
	
	# Title
	title = Paragraph('Attendance Report - Skola', styles['Title'])
	elements.append(title)
	elements.append(Spacer(1, 12))
	
	# Report info
	info_text = f"<b>Report Period:</b> {date_from or 'All'} to {date_to or 'All'}<br/>"
	info_text += f"<b>Total Records:</b> {total_records}<br/>"
	info = Paragraph(info_text, styles['Normal'])
	elements.append(info)
	elements.append(Spacer(1, 12))
	
	# Statistics table
	stats_data = [
		['Status', 'Count', 'Percentage'],
		['Present', status_stats.get(AttendanceRecord.Status.PRESENT, 0), 
		 f"{(status_stats.get(AttendanceRecord.Status.PRESENT, 0) / total_records * 100) if total_records > 0 else 0:.1f}%"],
		['Absent', status_stats.get(AttendanceRecord.Status.ABSENT, 0),
		 f"{(status_stats.get(AttendanceRecord.Status.ABSENT, 0) / total_records * 100) if total_records > 0 else 0:.1f}%"],
		['Late', status_stats.get(AttendanceRecord.Status.LATE, 0),
		 f"{(status_stats.get(AttendanceRecord.Status.LATE, 0) / total_records * 100) if total_records > 0 else 0:.1f}%"],
		['Excused', status_stats.get(AttendanceRecord.Status.EXCUSED, 0),
		 f"{(status_stats.get(AttendanceRecord.Status.EXCUSED, 0) / total_records * 100) if total_records > 0 else 0:.1f}%"],
	]
	
	stats_table = Table(stats_data)
	stats_table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.grey),
		('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
		('ALIGN', (0, 0), (-1, -1), 'CENTER'),
		('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
		('FONTSIZE', (0, 0), (-1, 0), 12),
		('BOTTOMPADDING', (0, 0), (-1, 0), 12),
		('BACKGROUND', (0, 1), (-1, -1), colors.beige),
		('GRID', (0, 0), (-1, -1), 1, colors.black),
	]))
	
	elements.append(stats_table)
	
	# Build PDF
	doc.build(elements)
	
	# Get PDF data
	pdf_data = buffer.getvalue()
	buffer.close()
	
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'
	response.write(pdf_data)
	
	return response


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def report_builder(request):
	"""
	Custom report builder for attendance reports.
	"""
	form = ReportBuilderForm(request.GET or None)
	records = None
	preview_records = []
	export_requested = request.GET.get('action') == 'export'
	template_loaded = False
	
	# Load template if requested
	template_id = request.GET.get('load_template')
	if template_id:
		try:
			template = ReportTemplate.objects.get(
				id=template_id,
				created_by=request.user if not request.user.is_superuser else None
			)
			# Pre-populate form with template data
			initial_data = {
				'report_name': template.name,
				'fields': template.fields,
				'grouping': template.grouping,
				'sorting': template.sorting,
			}
			# Load filters
			if template.filters:
				initial_data.update(template.filters)
			
			form = ReportBuilderForm(initial=initial_data)
			template_loaded = True
			messages.success(request, f'Template "{template.name}" loaded successfully.')
		except ReportTemplate.DoesNotExist:
			messages.error(request, 'Template not found.')
	
	if form.is_valid():
		# Build queryset based on filters
		records = AttendanceRecord.objects.select_related(
			'student', 'classroom', 'subject', 'recorded_by'
		)
		
		# Apply filters
		date_from = form.cleaned_data.get('date_from')
		date_to = form.cleaned_data.get('date_to')
		classroom = form.cleaned_data.get('classroom')
		subject = form.cleaned_data.get('subject')
		student = form.cleaned_data.get('student')
		status = form.cleaned_data.get('status')
		
		if date_from:
			records = records.filter(date__gte=date_from)
		if date_to:
			records = records.filter(date__lte=date_to)
		if classroom:
			records = records.filter(classroom=classroom)
		if subject:
			records = records.filter(subject=subject)
		if student:
			records = records.filter(student=student)
		if status:
			records = records.filter(status=status)
		
		# Save as template if requested
		if form.cleaned_data.get('save_as_template') and form.cleaned_data.get('report_name'):
			template = ReportTemplate.objects.create(
				name=form.cleaned_data['report_name'],
				created_by=request.user,
				fields=form.cleaned_data['fields'],
				filters={
					'date_from': date_from.isoformat() if date_from else None,
					'date_to': date_to.isoformat() if date_to else None,
					'classroom_id': classroom.id if classroom else None,
					'subject_id': subject.id if subject else None,
					'student_id': student.id if student else None,
					'status': status,
				},
				grouping=form.cleaned_data.get('grouping') or 'NONE',
				sorting=form.cleaned_data.get('sorting') or 'DATE_DESC',
			)
			messages.success(request, f'Report template "{template.name}" saved successfully.')
		
		# Export if requested
		if export_requested:
			generator = ReportGenerator(
				queryset=records,
				fields=form.cleaned_data['fields'],
				grouping=form.cleaned_data.get('grouping'),
				sorting=form.cleaned_data.get('sorting'),
				include_summary=form.cleaned_data.get('include_summary', True)
			)
			
			export_format = form.cleaned_data['export_format']
			
			try:
				if export_format == 'csv':
					return generator.export_csv()
				elif export_format == 'xlsx':
					return generator.export_xlsx()
				elif export_format == 'pdf':
					return generator.export_pdf()
			except ImportError as e:
				messages.error(request, str(e))
		else:
			# Preview mode - limit to 50 records
			preview_records = records[:50]
	
	# Get user's templates
	user_templates = ReportTemplate.objects.filter(created_by=request.user)
	shared_templates = ReportTemplate.objects.filter(is_shared=True).exclude(created_by=request.user)
	
	context = {
		'form': form,
		'preview_records': preview_records,
		'total_records': records.count() if records is not None else 0,
		'user_templates': user_templates,
		'shared_templates': shared_templates,
		'template_loaded': template_loaded,
	}
	
	return render(request, 'attendance/report_builder.html', context)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def template_list(request):
	"""List all report templates."""
	user_templates = ReportTemplate.objects.filter(created_by=request.user)
	shared_templates = ReportTemplate.objects.filter(is_shared=True).exclude(created_by=request.user)
	
	context = {
		'user_templates': user_templates,
		'shared_templates': shared_templates,
	}
	
	return render(request, 'attendance/template_list.html', context)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def template_delete(request, pk):
	"""Delete a report template."""
	template = get_object_or_404(ReportTemplate, pk=pk, created_by=request.user)
	
	if request.method == 'POST':
		template_name = template.name
		template.delete()
		messages.success(request, f'Template "{template_name}" deleted successfully.')
		return redirect('attendance:template_list')
	
	return render(request, 'attendance/template_confirm_delete.html', {'template': template})


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF, User.Role.TEACHER)
def template_update(request, pk):
	"""Update a report template."""
	template = get_object_or_404(ReportTemplate, pk=pk, created_by=request.user)
	
	if request.method == 'POST':
		form = ReportTemplateForm(request.POST, instance=template)
		if form.is_valid():
			form.save()
			messages.success(request, f'Template "{template.name}" updated successfully.')
			return redirect('attendance:template_list')
	else:
		form = ReportTemplateForm(instance=template)
	
	return render(request, 'attendance/template_form.html', {'form': form, 'template': template})


@login_required
@role_required(User.Role.GUARDIAN)
def notification_preferences(request):
	"""View and edit notification preferences for guardians."""
	user = request.user
	
	# Get or create preferences
	try:
		prefs = user.notification_preferences
	except NotificationPreference.DoesNotExist:
		prefs = NotificationPreference.objects.create(user=user)
	
	if request.method == 'POST':
		form = NotificationPreferenceForm(request.POST, instance=prefs)
		if form.is_valid():
			form.save()
			messages.success(request, 'Notification preferences updated successfully.')
			return redirect('attendance:notification_preferences')
	else:
		form = NotificationPreferenceForm(instance=prefs)
	
	# Get email log for this user
	recent_emails = user.email_logs.all()[:10]
	
	return render(
		request,
		'attendance/notification_preferences.html',
		{
			'form': form,
			'preferences': prefs,
			'recent_emails': recent_emails,
		}
	)
