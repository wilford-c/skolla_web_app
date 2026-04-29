"""WebSocket consumers for real-time messaging."""

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Conversation
from .models import Message
from .models import MessageRead
from .realtime import serialize_message
from .user_status import decrement_active_socket
from .user_status import increment_active_socket
from .user_status import is_user_online


class ConversationConsumer(AsyncJsonWebsocketConsumer):
    """Handle chat messages, typing indicators, and presence updates."""

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close(code=4401)
            return

        self.conversation_id = int(self.scope["url_route"]["kwargs"]["conversation_id"])
        self.group_name = f"conversation_{self.conversation_id}"

        is_allowed = await self._is_participant(self.user.id, self.conversation_id)
        if not is_allowed:
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await database_sync_to_async(increment_active_socket)(self.user.id)

        presence_snapshot = await self._get_presence_snapshot(
            conversation_id=self.conversation_id,
            current_user_id=self.user.id,
        )
        await self.send_json(
            {
                "type": "presence_snapshot",
                "participants": presence_snapshot,
            }
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "presence.update",
                "user_id": self.user.id,
                "display_name": self.user.display_name,
                "status": "online",
            },
        )

    async def disconnect(self, close_code):
        if getattr(self, "group_name", None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

        if getattr(self, "user", None) and self.user.is_authenticated:
            remaining_connections = await database_sync_to_async(decrement_active_socket)(self.user.id)
            if remaining_connections == 0 and getattr(self, "group_name", None):
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "presence.update",
                        "user_id": self.user.id,
                        "display_name": self.user.display_name,
                        "status": "offline",
                    },
                )

    async def receive_json(self, content, **kwargs):
        event_type = content.get("type")

        if event_type == "chat_message":
            message_text = (content.get("content") or "").strip()
            if not message_text:
                return

            message_payload = await self._create_message(
                conversation_id=self.conversation_id,
                user_id=self.user.id,
                content=message_text,
            )
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.message",
                    "message": message_payload,
                },
            )
            return

        if event_type == "typing":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "typing.update",
                    "user_id": self.user.id,
                    "display_name": self.user.display_name,
                    "is_typing": True,
                },
            )
            return

        if event_type == "stop_typing":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "typing.update",
                    "user_id": self.user.id,
                    "display_name": self.user.display_name,
                    "is_typing": False,
                },
            )
            return

        if event_type == "mark_read":
            message_id = content.get("message_id")
            if message_id:
                try:
                    message_id = int(message_id)
                except (TypeError, ValueError):
                    return

                read_receipt_payload = await self._mark_read(
                    message_id=message_id,
                    user_id=self.user.id,
                    conversation_id=self.conversation_id,
                )
                if read_receipt_payload:
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            "type": "read.receipt",
                            "payload": read_receipt_payload,
                        },
                    )

    async def chat_message(self, event):
        await self.send_json(
            {
                "type": "chat_message",
                "message": event["message"],
            }
        )

    async def typing_update(self, event):
        if event["user_id"] == self.user.id:
            return

        await self.send_json(
            {
                "type": "typing_update",
                "user_id": event["user_id"],
                "display_name": event["display_name"],
                "is_typing": event["is_typing"],
            }
        )

    async def presence_update(self, event):
        if event["user_id"] == self.user.id:
            return

        await self.send_json(
            {
                "type": "presence_update",
                "user_id": event["user_id"],
                "display_name": event["display_name"],
                "status": event["status"],
            }
        )

    async def read_receipt(self, event):
        if event["payload"]["user_id"] == self.user.id:
            return

        await self.send_json(
            {
                "type": "read_receipt",
                "payload": event["payload"],
            }
        )

    @database_sync_to_async
    def _is_participant(self, user_id, conversation_id):
        return Conversation.objects.filter(id=conversation_id, participants__id=user_id).exists()

    @database_sync_to_async
    def _create_message(self, conversation_id, user_id, content):
        conversation = Conversation.objects.get(id=conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender_id=user_id,
            content=content,
        )
        conversation.save(update_fields=["updated_at"])
        return serialize_message(message)

    @database_sync_to_async
    def _get_presence_snapshot(self, conversation_id, current_user_id):
        conversation = Conversation.objects.prefetch_related("participants").get(id=conversation_id)
        snapshot = []
        for participant in conversation.participants.all():
            snapshot.append(
                {
                    "user_id": participant.id,
                    "display_name": participant.display_name,
                    "status": "online"
                    if participant.id == current_user_id or is_user_online(participant.id)
                    else "offline",
                }
            )
        return snapshot

    @database_sync_to_async
    def _mark_read(self, message_id, user_id, conversation_id):
        try:
            message = Message.objects.select_related("sender").get(
                id=message_id,
                conversation_id=conversation_id,
            )
        except Message.DoesNotExist:
            return None

        if message.sender_id == user_id:
            return None

        _, created = MessageRead.objects.get_or_create(message_id=message_id, user_id=user_id)
        if not created:
            return None

        return {
            "message_id": message_id,
            "user_id": user_id,
        }
