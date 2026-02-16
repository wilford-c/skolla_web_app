from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required

from .forms import ClassroomForm, SubjectForm
from .models import Classroom, Subject

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
		form.save()
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
		form.save()
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
	classroom.delete()
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
		form.save()
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
		form.save()
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
	subject.delete()
	messages.success(request, 'Subject deleted successfully.')
	return redirect('academics:subjects')
