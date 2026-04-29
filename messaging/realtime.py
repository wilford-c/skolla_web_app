"""Helpers for broadcasting messaging events over Channels."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def serialize_message(message):
    """Return a websocket-safe payload for a Message instance."""
    sender = message.sender
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "sender_id": sender.id,
        "sender_name": sender.display_name,
        "sender_role": sender.get_role_display(),
        "content": message.content,
        "sent_at": message.sent_at.isoformat(),
    }


def broadcast_new_message(message):
    """Broadcast a newly created message to all conversation participants."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        f"conversation_{message.conversation_id}",
        {
            "type": "chat.message",
            "message": serialize_message(message),
        },
    )
