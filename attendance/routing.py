"""WebSocket routing for attendance app."""

from django.urls import re_path

from .consumers import AttendanceDashboardConsumer

websocket_urlpatterns = [
    re_path(r"^ws/dashboard/attendance/$", AttendanceDashboardConsumer.as_asgi()),
]
