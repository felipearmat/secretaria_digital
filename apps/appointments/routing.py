"""
WebSocket routing configuration for the appointments app.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/appointments/(?P<room_name>\w+)/$', consumers.AppointmentConsumer.as_asgi()),
    re_path(r'ws/notifications/(?P<user_id>\w+)/$', consumers.NotificationConsumer.as_asgi()),
]
