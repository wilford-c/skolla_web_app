from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required

from .forms import AttendanceForm
from .models import AttendanceRecord

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
		form.save()
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
	record.delete()
	messages.success(request, 'Attendance record deleted successfully.')
	return redirect('attendance:list')
