from __future__ import annotations

from typing import Any

from .models import AuditEvent


def _request_ip(request) -> str | None:
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_event(
    *,
    request,
    action: str,
    entity_type: str = "",
    entity_id: str = "",
    description: str = "",
    metadata: dict[str, Any] | None = None,
    severity: str = AuditEvent.Severity.INFO,
) -> None:
    """Persist an audit event without breaking the caller path on failures."""
    try:
        AuditEvent.objects.create(
            user=request.user if getattr(request.user, "is_authenticated", False) else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            metadata=metadata or {},
            severity=severity,
            ip_address=_request_ip(request),
        )
    except Exception:
        # Audit logging should never block business operations.
        return
