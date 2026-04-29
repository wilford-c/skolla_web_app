from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.decorators import role_required

from .models import AuditEvent

User = get_user_model()


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF)
def audit_event_list(request):
    events = AuditEvent.objects.select_related("user").all()

    q = request.GET.get("q", "").strip()
    action = request.GET.get("action", "").strip()
    entity_type = request.GET.get("entity", "").strip()

    if q:
        events = events.filter(description__icontains=q)
    if action:
        events = events.filter(action=action)
    if entity_type:
        events = events.filter(entity_type=entity_type)

    context = {
        "events": events[:200],
        "query": q,
        "selected_action": action,
        "selected_entity": entity_type,
        "actions": AuditEvent.objects.values_list("action", flat=True).distinct().order_by("action"),
        "entities": AuditEvent.objects.values_list("entity_type", flat=True)
        .exclude(entity_type="")
        .distinct()
        .order_by("entity_type"),
    }
    return render(request, "auditlog/event_list.html", context)
