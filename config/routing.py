"""Project-wide websocket URL routing."""

from attendance.routing import websocket_urlpatterns as attendance_websocket_urlpatterns
from messaging.routing import websocket_urlpatterns as messaging_websocket_urlpatterns
from notifications.routing import websocket_urlpatterns as notifications_websocket_urlpatterns

websocket_urlpatterns = [
    *messaging_websocket_urlpatterns,
    *notifications_websocket_urlpatterns,
    *attendance_websocket_urlpatterns,
]
