from collections import defaultdict
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render
from django.utils import timezone

from academics.models import Classroom, Subject
from attendance.models import AttendanceRecord
from billing.models import FeeInvoice
from students.models import Student

from .forms import LoginForm, UserRegistrationForm, UserProfileForm, CustomPasswordChangeForm


User = get_user_model()


def register_view(request):
	if request.user.is_authenticated:
		return redirect('accounts:dashboard')

	form = UserRegistrationForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		form.save()
		messages.success(request, 'Account created successfully. You can log in now.')
		return redirect('accounts:login')

	return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
	if request.user.is_authenticated:
		return redirect('accounts:dashboard')

	form = LoginForm(request, data=request.POST or None)
	if request.method == 'POST' and form.is_valid():
		user = form.get_user()
		auth_login(request, user)
		if not form.cleaned_data.get('remember_me'):
			request.session.set_expiry(0)
		messages.success(request, f'Welcome back, {user.display_name}!')
		return redirect('accounts:dashboard')

	return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
	auth_logout(request)
	messages.info(request, 'You have been signed out.')
	return redirect('accounts:login')


@login_required
def dashboard_view(request):
	user = request.user
	role = getattr(user, 'role', User.Role.STAFF)
	is_admin_portal = user.is_superuser or role in (User.Role.ADMIN, User.Role.STAFF)
	context = {
		'is_admin_portal': is_admin_portal,
		'is_teacher_portal': role == User.Role.TEACHER,
		'is_student_portal': role == User.Role.STUDENT,
		'is_guardian_portal': role == User.Role.GUARDIAN,
		'can_record_attendance': user.is_superuser or role in (
			User.Role.ADMIN,
			User.Role.STAFF,
			User.Role.TEACHER,
		),
	}

	if context['is_admin_portal']:
		student_count = Student.objects.count()
		class_count = Classroom.objects.count()
		subject_count = Subject.objects.count()
		recent_attendance = (
			AttendanceRecord.objects.select_related('student', 'classroom', 'subject')
			.order_by('-date')[:5]
		)
		
		# Attendance statistics for the last 7 days
		from datetime import timedelta
		from django.utils import timezone
		seven_days_ago = timezone.now().date() - timedelta(days=7)
		
		attendance_stats = (
			AttendanceRecord.objects.filter(date__gte=seven_days_ago)
			.values('status')
			.annotate(count=Count('id'))
		)
		attendance_summary = {item['status']: item['count'] for item in attendance_stats}
		total_attendance_records = sum(attendance_summary.values())
		invoice_totals = FeeInvoice.objects.aggregate(
			total_billed=Coalesce(Sum('amount_due'), Decimal('0.00')),
			total_collected=Coalesce(Sum('amount_paid'), Decimal('0.00')),
		)
		overdue_invoice_count = FeeInvoice.objects.filter(
			status__in=[FeeInvoice.Status.UNPAID, FeeInvoice.Status.PARTIAL],
			due_date__lt=timezone.localdate(),
		).count()
		
		context.update(
			{
				'student_count': student_count,
				'class_count': class_count,
				'subject_count': subject_count,
				'recent_attendance': recent_attendance,
				'attendance_summary': attendance_summary,
				'total_attendance_records': total_attendance_records,
				'present_count': attendance_summary.get(AttendanceRecord.Status.PRESENT, 0),
				'absent_count': attendance_summary.get(AttendanceRecord.Status.ABSENT, 0),
				'late_count': attendance_summary.get(AttendanceRecord.Status.LATE, 0),
				'total_billed': invoice_totals['total_billed'],
				'total_collected': invoice_totals['total_collected'],
				'total_outstanding': invoice_totals['total_billed'] - invoice_totals['total_collected'],
				'overdue_invoice_count': overdue_invoice_count,
			}
		)
	elif context['is_teacher_portal']:
		teacher_classes = Classroom.objects.filter(
			Q(homeroom_teacher=user) | Q(subjects__teacher=user)
		).distinct()
		teacher_subjects = Subject.objects.filter(teacher=user).select_related('classroom')
		recent_attendance = (
			AttendanceRecord.objects
			.filter(recorded_by=user)
			.select_related('student', 'classroom', 'subject')
			.order_by('-date')[:5]
		)
		context.update(
			{
				'teacher_classes': teacher_classes,
				'teacher_subjects': teacher_subjects,
				'recent_attendance': recent_attendance,
			}
		)
	elif context['is_student_portal']:
		student_profile = getattr(user, 'student_profile', None)
		if student_profile:
			attendance_qs = (
				student_profile.attendance_records.select_related('classroom', 'subject').order_by('-date')
			)
			attendance_summary = {
				entry['status']: entry['total']
				for entry in attendance_qs.values('status').annotate(total=Count('id'))
			}
			invoice_totals = FeeInvoice.objects.filter(student=student_profile).aggregate(
				total_due=Coalesce(Sum('amount_due'), Decimal('0.00')),
				total_paid=Coalesce(Sum('amount_paid'), Decimal('0.00')),
			)
			overdue_invoices = FeeInvoice.objects.filter(
				student=student_profile,
				status__in=[FeeInvoice.Status.UNPAID, FeeInvoice.Status.PARTIAL],
				due_date__lt=timezone.localdate(),
			).count()
			context.update(
				{
					'student_profile': student_profile,
					'student_recent_attendance': list(attendance_qs[:5]),
					'student_attendance_summary': attendance_summary,
					'student_invoice_due': invoice_totals['total_due'],
					'student_invoice_paid': invoice_totals['total_paid'],
					'student_invoice_outstanding': invoice_totals['total_due'] - invoice_totals['total_paid'],
					'student_overdue_invoices': overdue_invoices,
				}
			)
		else:
			context['student_profile'] = None
	elif context['is_guardian_portal']:
		from academics.models import Grade
		
		guardian_students = Student.objects.filter(guardian_user=user).prefetch_related(
			Prefetch(
				'attendance_records',
				queryset=AttendanceRecord.objects.select_related('classroom', 'subject').order_by('-date'),
			)
		)
		summary_map = defaultdict(dict)
		for row in (
			AttendanceRecord.objects.filter(student__guardian_user=user)
			.values('student_id', 'status')
			.annotate(total=Count('id'))
		):
			summary_map[row['student_id']][row['status']] = row['total']
		invoice_map = {
			row['student_id']: row
			for row in (
				FeeInvoice.objects.filter(student__guardian_user=user)
				.values('student_id')
				.annotate(
					total_due=Coalesce(Sum('amount_due'), Decimal('0.00')),
					total_paid=Coalesce(Sum('amount_paid'), Decimal('0.00')),
					overdue_count=Count(
						'id',
						filter=Q(
							status__in=[FeeInvoice.Status.UNPAID, FeeInvoice.Status.PARTIAL],
							due_date__lt=timezone.localdate(),
						),
					),
				)
			)
		}
		
		# Calculate grade statistics for each child
		children_data = []
		for student in guardian_students:
			# Get grades for this student
			grades = Grade.objects.filter(student=student).select_related(
				'assessment',
				'assessment__subject',
			)
			
			# Calculate overall average
			if grades.exists():
				total_percentage = sum(grade.percentage for grade in grades)
				average_percentage = total_percentage / grades.count()
			else:
				average_percentage = None
			
			children_data.append({
				'student': student,
				'recent_records': list(student.attendance_records.all()[:5]),
				'attendance_summary': summary_map.get(student.id, {}),
				'grade_count': grades.count(),
				'average_percentage': round(average_percentage, 1) if average_percentage is not None else None,
				'invoice_due': invoice_map.get(student.id, {}).get('total_due', Decimal('0.00')),
				'invoice_paid': invoice_map.get(student.id, {}).get('total_paid', Decimal('0.00')),
				'invoice_outstanding': (
					invoice_map.get(student.id, {}).get('total_due', Decimal('0.00'))
					- invoice_map.get(student.id, {}).get('total_paid', Decimal('0.00'))
				),
				'overdue_invoice_count': invoice_map.get(student.id, {}).get('overdue_count', 0),
			})
		
		context['guardian_children'] = children_data

	return render(request, 'dashboard.html', context)


@login_required
def profile_view(request):
	"""Display user profile."""
	return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def profile_edit_view(request):
	"""Edit user profile information."""
	if request.method == 'POST':
		form = UserProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			messages.success(request, 'Your profile has been updated successfully.')
			return redirect('accounts:profile')
	else:
		form = UserProfileForm(instance=request.user)
	
	return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def password_change_view(request):
	"""Change user password."""
	if request.method == 'POST':
		form = CustomPasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			from django.contrib.auth import update_session_auth_hash
			update_session_auth_hash(request, user)
			messages.success(request, 'Your password has been changed successfully.')
			return redirect('accounts:profile')
	else:
		form = CustomPasswordChangeForm(request.user)
	
	return render(request, 'accounts/password_change.html', {'form': form})
