"""Helpers for pushing real-time notification updates."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def get_unread_count(user_id):
    """Return unread notification count for a user."""
    return Notification.objects.filter(recipient_id=user_id, is_read=False).count()


def push_unread_count(user_id):
    """Push unread count update to the user's notifications websocket group."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    unread_count = get_unread_count(user_id)
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}_notifications",
        {
            "type": "notification.count",
            "count": unread_count,
        },
    )
