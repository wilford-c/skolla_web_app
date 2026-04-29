from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Notification
from .realtime import get_unread_count, push_unread_count


@login_required
def notification_list(request):
    """Display user's notifications."""
    notifications = request.user.notifications.all()[:50]  # Last 50 notifications
    
    return render(request, 'notifications/list.html', {
        'notifications': notifications,
    })


@login_required
def unread_count(request):
    """Get count of unread notifications (AJAX/HTMX endpoint)."""
    count = get_unread_count(request.user.id)
    
    # Return HTML partial for HTMX requests
    if request.headers.get('HX-Request'):
        return render(request, 'notifications/partials/badge.html', {'count': count})
    
    # Return JSON for traditional AJAX
    return JsonResponse({'count': count})


@login_required
@require_POST
def mark_notification_read(request, pk):
    """Mark a single notification as read."""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    # Redirect to action URL if available
    if notification.action_url:
        return redirect(notification.action_url)
    
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    """Mark all notifications as read."""
    request.user.notifications.filter(is_read=False).update(is_read=True, read_at=timezone.now())
    push_unread_count(request.user.id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:list')
