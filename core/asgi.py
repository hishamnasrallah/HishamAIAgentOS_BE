"""
ASGI config for HishamOS project.
Supports both HTTP and WebSocket protocols.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

# Initialize Django ASGI application early to populate apps registry
django_asgi_app = get_asgi_application()

# Import websocket routing after Django initialization
from apps.monitoring import routing as monitoring_routing
from apps.chat import routing as chat_routing
from apps.agents import routing as agents_routing
from apps.workflows import routing as workflows_routing
from apps.projects import routing as projects_routing
from core.middleware import JWTAuthMiddlewareStack

# WebSocket routing with authentication
websocket_router = URLRouter(
    monitoring_routing.websocket_urlpatterns +
    chat_routing.websocket_urlpatterns +
    agents_routing.websocket_urlpatterns +
    workflows_routing.websocket_urlpatterns +
    projects_routing.websocket_urlpatterns
)

# Apply middleware stack
# Note: AuthMiddlewareStack must be outermost to handle session auth
# JWTAuthMiddlewareStack is inside to handle JWT tokens
websocket_stack = AuthMiddlewareStack(
    JWTAuthMiddlewareStack(websocket_router)
)

# In development, allow all origins for WebSocket
# In production, use AllowedHostsOriginValidator
if os.environ.get('DJANGO_SETTINGS_MODULE', '').endswith('development'):
    websocket_app = websocket_stack
else:
    websocket_app = AllowedHostsOriginValidator(websocket_stack)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": websocket_app,
})
