"""
WebSocket URL routing for workflows app.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Match with trailing slash (like chat routing)  
    re_path(r'ws/workflows/execution/(?P<execution_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', consumers.WorkflowExecutionConsumer.as_asgi()),
    # Also match without trailing slash
    re_path(r'ws/workflows/execution/(?P<execution_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$', consumers.WorkflowExecutionConsumer.as_asgi()),
]

