from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required

from .forms import StudentForm
from .models import Student

User = get_user_model()


@login_required
def student_list(request):
	students = Student.objects.select_related('user', 'guardian_user').all()
	can_manage = request.user.is_superuser or request.user.role == User.Role.ADMIN
	can_create = can_manage or request.user.role == User.Role.STAFF
	return render(
		request,
		'students/student_list.html',
		{
			'students': students,
			'can_manage_students': can_manage,
			'can_create_students': can_create,
		},
	)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF)
def student_create(request):
	form = StudentForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		form.save()
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
	student = get_object_or_404(Student, pk=pk)
	form = StudentForm(request.POST or None, instance=student)
	if request.method == 'POST' and form.is_valid():
		form.save()
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
@role_required(User.Role.ADMIN)
@require_POST
def student_delete(request, pk):
	student = get_object_or_404(Student, pk=pk)
	student.delete()
	messages.success(request, 'Student profile deleted successfully.')
	return redirect('students:list')
