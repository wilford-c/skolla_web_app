from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from auditlog.services import log_event

from .models import Assignment, Submission, AssignmentAttachment, SubmissionFile
from .forms import AssignmentForm


def can_manage_assignments(user):
    """Check if user can create/edit/delete assignments."""
    return user.is_authenticated and user.role in ['TEACHER', 'ADMIN', 'STAFF']


@login_required
def assignment_list(request):
    """List assignments for the current user."""
    user = request.user
    
    if user.role == 'TEACHER':
        assignments = Assignment.objects.filter(teacher=user).order_by('-assigned_date')
    elif user.role == 'STUDENT':
        student_profile = getattr(user, 'student_profile', None)
        if student_profile and student_profile.current_classroom_id:
            assignments = Assignment.objects.filter(
                classroom=student_profile.current_classroom,
                status=Assignment.Status.PUBLISHED,
            ).order_by('-assigned_date')
        else:
            assignments = Assignment.objects.none()
    else:
        assignments = Assignment.objects.all().order_by('-assigned_date')
    
    return render(request, 'assignments/list.html', {
        'assignments': assignments,
    })


@login_required
def assignment_detail(request, pk):
    """View assignment details."""
    assignment = get_object_or_404(Assignment, pk=pk)
    
    submissions = assignment.submissions.select_related('student__user').all()
    
    return render(request, 'assignments/detail.html', {
        'assignment': assignment,
        'submissions': submissions,
    })


@login_required
def submit_assignment(request, pk):
    """Submit an assignment (student only)."""
    assignment = get_object_or_404(Assignment, pk=pk)
    student_profile = getattr(request.user, 'student_profile', None)
    
    if not student_profile:
        messages.error(request, 'Only students can submit assignments.')
        return redirect('assignments:list')
    
    if request.method == 'POST':
        content = request.POST.get('content', '')
        
        submission, created = Submission.objects.get_or_create(
            assignment=assignment,
            student=student_profile,
            defaults={'content': content}
        )
        
        if not created:
            submission.content = content
            submission.save()

        log_event(
            request=request,
            action='assignment.submit',
            entity_type='Submission',
            entity_id=str(submission.pk),
            description=f'Submission saved for assignment "{assignment.title}" by {student_profile.admission_number}.',
            metadata={'assignment_id': assignment.pk},
        )
        
        messages.success(request, 'Assignment submitted successfully!')
        return redirect('assignments:detail', pk=assignment.pk)
    
    return render(request, 'assignments/submit.html', {
        'assignment': assignment,
    })


@login_required
@user_passes_test(can_manage_assignments, login_url='/accounts/login/')
def create_assignment(request):
    """Create a new assignment (Teacher/Admin/Staff only)."""
    if request.method == 'POST':
        form = AssignmentForm(request.POST, user=request.user)
        
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = request.user
            assignment.save()
            
            # Handle file uploads
            files = request.FILES.getlist('attachments')
            for file in files:
                AssignmentAttachment.objects.create(
                    assignment=assignment,
                    file=file,
                    filename=file.name
                )

            log_event(
                request=request,
                action='assignment.create',
                entity_type='Assignment',
                entity_id=str(assignment.pk),
                description=f'Created assignment "{assignment.title}".',
                metadata={
                    'classroom_id': assignment.classroom_id,
                    'subject_id': assignment.subject_id,
                    'status': assignment.status,
                },
            )
            
            messages.success(request, f'Assignment "{assignment.title}" created successfully!')
            return redirect('assignments:detail', pk=assignment.pk)
    else:
        form = AssignmentForm(user=request.user)
    
    return render(request, 'assignments/create.html', {
        'form': form,
        'action': 'Create',
    })


@login_required
@user_passes_test(can_manage_assignments, login_url='/accounts/login/')
def edit_assignment(request, pk):
    """Edit an existing assignment (Teacher/Admin/Staff only)."""
    assignment = get_object_or_404(Assignment, pk=pk)
    
    # Only allow teacher who created it, or admins/staff to edit
    if request.user.role == 'TEACHER' and assignment.teacher != request.user:
        messages.error(request, 'You can only edit your own assignments.')
        return redirect('assignments:detail', pk=assignment.pk)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment, user=request.user)
        
        if form.is_valid():
            assignment = form.save()
            
            # Handle file uploads
            files = request.FILES.getlist('attachments')
            for file in files:
                AssignmentAttachment.objects.create(
                    assignment=assignment,
                    file=file,
                    filename=file.name
                )
            
            # Handle file deletions
            delete_attachments = request.POST.getlist('delete_attachment')
            if delete_attachments:
                AssignmentAttachment.objects.filter(
                    id__in=delete_attachments
                ).delete()

            log_event(
                request=request,
                action='assignment.update',
                entity_type='Assignment',
                entity_id=str(assignment.pk),
                description=f'Updated assignment "{assignment.title}".',
                metadata={
                    'classroom_id': assignment.classroom_id,
                    'subject_id': assignment.subject_id,
                    'status': assignment.status,
                },
            )
            
            messages.success(request, f'Assignment "{assignment.title}" updated successfully!')
            return redirect('assignments:detail', pk=assignment.pk)
    else:
        form = AssignmentForm(instance=assignment, user=request.user)
    
    return render(request, 'assignments/create.html', {
        'form': form,
        'assignment': assignment,
        'action': 'Edit',
    })


@login_required
@user_passes_test(can_manage_assignments, login_url='/accounts/login/')
def delete_assignment(request, pk):
    """Delete an assignment (Teacher/Admin/Staff only)."""
    assignment = get_object_or_404(Assignment, pk=pk)
    
    # Only allow teacher who created it, or admins/staff to delete
    if request.user.role == 'TEACHER' and assignment.teacher != request.user:
        messages.error(request, 'You can only delete your own assignments.')
        return redirect('assignments:detail', pk=assignment.pk)
    
    if request.method == 'POST':
        title = assignment.title
        assignment_id = str(assignment.pk)
        assignment.delete()
        log_event(
            request=request,
            action='assignment.delete',
            entity_type='Assignment',
            entity_id=assignment_id,
            description=f'Deleted assignment "{title}".',
            severity='WARNING',
        )
        messages.success(request, f'Assignment "{title}" deleted successfully!')
        return redirect('assignments:list')
    
    return render(request, 'assignments/delete.html', {
        'assignment': assignment,
    })
