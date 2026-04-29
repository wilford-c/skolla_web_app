"""WebSocket consumer for live notifications badge updates."""

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .realtime import get_unread_count


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """Send instant unread count updates to authenticated users."""

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close(code=4401)
            return

        self.group_name = f"user_{self.user.id}_notifications"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        unread_count = await database_sync_to_async(get_unread_count)(self.user.id)
        await self.send_json(
            {
                "type": "notification_count",
                "count": unread_count,
            }
        )

    async def disconnect(self, close_code):
        if getattr(self, "group_name", None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notification_count(self, event):
        await self.send_json(
            {
                "type": "notification_count",
                "count": event["count"],
            }
        )
