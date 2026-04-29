"""WebSocket consumers for real-time attendance dashboard updates."""

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from accounts.models import User

from .realtime import get_admin_dashboard_payload


class AttendanceDashboardConsumer(AsyncJsonWebsocketConsumer):
    """Push live attendance summary updates to admin/staff dashboards."""

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close(code=4401)
            return

        can_access = await self._can_access_dashboard(self.user.id)
        if not can_access:
            await self.close(code=4403)
            return

        self.group_name = "attendance_dashboard_admin"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        payload = await database_sync_to_async(get_admin_dashboard_payload)()
        await self.send_json(
            {
                "type": "attendance_dashboard",
                "payload": payload,
            }
        )

    async def disconnect(self, close_code):
        if getattr(self, "group_name", None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def attendance_dashboard(self, event):
        await self.send_json(
            {
                "type": "attendance_dashboard",
                "payload": event["payload"],
            }
        )

    @database_sync_to_async
    def _can_access_dashboard(self, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return False

        return user.is_superuser or user.role in {User.Role.ADMIN, User.Role.STAFF}
