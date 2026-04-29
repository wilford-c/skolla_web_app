"""Helpers for pushing attendance dashboard updates over Channels."""

from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Count
from django.utils import timezone

from .models import AttendanceRecord


def get_admin_dashboard_payload():
    """Return summary and latest record details for the admin attendance widget."""
    seven_days_ago = timezone.now().date() - timedelta(days=7)
    stats = (
        AttendanceRecord.objects.filter(date__gte=seven_days_ago)
        .values("status")
        .annotate(count=Count("id"))
    )
    summary = {item["status"]: item["count"] for item in stats}

    latest_record = (
        AttendanceRecord.objects.select_related("student", "classroom")
        .order_by("-recorded_at")
        .first()
    )
    latest_payload = None
    if latest_record is not None:
        latest_payload = {
            "id": latest_record.id,
            "student_name": latest_record.student.full_name,
            "classroom": str(latest_record.classroom),
            "status": latest_record.status,
            "status_display": latest_record.get_status_display(),
            "date": latest_record.date.isoformat(),
        }

    return {
        "present_count": summary.get(AttendanceRecord.Status.PRESENT, 0),
        "absent_count": summary.get(AttendanceRecord.Status.ABSENT, 0),
        "late_count": summary.get(AttendanceRecord.Status.LATE, 0),
        "total_attendance_records": sum(summary.values()),
        "latest_record": latest_payload,
        "updated_at": timezone.now().isoformat(),
    }


def push_admin_dashboard_update():
    """Broadcast attendance dashboard changes to connected admin/staff clients."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        "attendance_dashboard_admin",
        {
            "type": "attendance.dashboard",
            "payload": get_admin_dashboard_payload(),
        },
    )
