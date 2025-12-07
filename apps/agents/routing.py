"""
WebSocket URL routing for agents app.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/agents/execution/(?P<execution_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', consumers.AgentExecutionConsumer.as_asgi()),
]

