"""
WebSocket routing for projects app.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/projects/(?P<project_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/collaborate/$',
        consumers.CollaborativeEditingConsumer.as_asgi()
    ),
]

