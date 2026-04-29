from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from auditlog.services import log_event

from .models import Announcement, AnnouncementView, AnnouncementAttachment
from .forms import AnnouncementForm, AnnouncementAttachmentFormSet


def is_admin_or_staff(user):
    """Check if user is admin or staff."""
    return user.is_authenticated and user.role in ['ADMIN', 'STAFF']


@login_required
def announcement_list(request):
    """Display list of announcements for the current user."""
    user = request.user
    
    # Filter announcements based on user role
    announcements_qs = Announcement.objects.filter(published=True)
    
    if user.role == 'STUDENT':
        announcements_qs = announcements_qs.filter(
            audience__in=['ALL', 'STUDENTS']
        )
    elif user.role == 'TEACHER':
        announcements_qs = announcements_qs.filter(
            audience__in=['ALL', 'TEACHERS']
        )
    elif user.role == 'GUARDIAN':
        announcements_qs = announcements_qs.filter(
            audience__in=['ALL', 'GUARDIANS']
        )
    elif user.role in ['ADMIN', 'STAFF'] or user.is_superuser:
        pass  # Admins see all
    
    announcements_qs = announcements_qs.select_related('author').prefetch_related('attachments')
    
    # Mark viewed announcements
    viewed_ids = AnnouncementView.objects.filter(user=user).values_list('announcement_id', flat=True)
    
    return render(request, 'announcements/list.html', {
        'announcements': announcements_qs,
        'viewed_ids': list(viewed_ids),
    })


@login_required
def announcement_detail(request, pk):
    """Display a single announcement and mark as viewed."""
    announcement = get_object_or_404(Announcement, pk=pk, published=True)
    
    # Mark as viewed
    AnnouncementView.objects.get_or_create(
        announcement=announcement,
        user=request.user
    )
    
    return render(request, 'announcements/detail.html', {
        'announcement': announcement,
    })


@login_required
@user_passes_test(is_admin_or_staff, login_url='/accounts/login/')
def create_announcement(request):
    """Create a new announcement (Admin/Staff only)."""
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            announcement.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Handle file uploads
            files = request.FILES.getlist('attachments')
            for file in files:
                AnnouncementAttachment.objects.create(
                    announcement=announcement,
                    file=file,
                    filename=file.name
                )

            log_event(
                request=request,
                action='announcement.create',
                entity_type='Announcement',
                entity_id=str(announcement.pk),
                description=f'Created announcement "{announcement.title}".',
                metadata={
                    'audience': announcement.audience,
                    'priority': announcement.priority,
                },
            )
            
            messages.success(request, f'Announcement "{announcement.title}" created successfully!')
            return redirect('announcements:detail', pk=announcement.pk)
    else:
        form = AnnouncementForm()
    
    return render(request, 'announcements/create.html', {
        'form': form,
        'action': 'Create',
    })


@login_required
@user_passes_test(is_admin_or_staff, login_url='/accounts/login/')
def edit_announcement(request, pk):
    """Edit an existing announcement (Admin/Staff only)."""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        
        if form.is_valid():
            announcement = form.save()
            
            # Handle file uploads
            files = request.FILES.getlist('attachments')
            for file in files:
                AnnouncementAttachment.objects.create(
                    announcement=announcement,
                    file=file,
                    filename=file.name
                )
            
            # Handle file deletions
            delete_attachments = request.POST.getlist('delete_attachment')
            if delete_attachments:
                AnnouncementAttachment.objects.filter(
                    id__in=delete_attachments
                ).delete()

            log_event(
                request=request,
                action='announcement.update',
                entity_type='Announcement',
                entity_id=str(announcement.pk),
                description=f'Updated announcement "{announcement.title}".',
                metadata={
                    'audience': announcement.audience,
                    'priority': announcement.priority,
                    'published': announcement.published,
                },
            )
            
            messages.success(request, f'Announcement "{announcement.title}" updated successfully!')
            return redirect('announcements:detail', pk=announcement.pk)
    else:
        form = AnnouncementForm(instance=announcement)
    
    return render(request, 'announcements/create.html', {
        'form': form,
        'announcement': announcement,
        'action': 'Edit',
    })


@login_required
@user_passes_test(is_admin_or_staff, login_url='/accounts/login/')
def delete_announcement(request, pk):
    """Delete an announcement (Admin/Staff only)."""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.method == 'POST':
        title = announcement.title
        announcement_id = str(announcement.pk)
        announcement.delete()
        log_event(
            request=request,
            action='announcement.delete',
            entity_type='Announcement',
            entity_id=announcement_id,
            description=f'Deleted announcement "{title}".',
            severity='WARNING',
        )
        messages.success(request, f'Announcement "{title}" deleted successfully!')
        return redirect('announcements:list')
    
    return render(request, 'announcements/delete.html', {
        'announcement': announcement,
    })
