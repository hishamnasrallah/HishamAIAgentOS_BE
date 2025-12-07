"""
JWT authentication middleware for WebSocket connections.
"""

import logging
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_string):
    """Get user from JWT token."""
    try:
        logger.info(f"[JWT Middleware] Attempting to authenticate with token")
        access_token = AccessToken(token_string)
        user_id = access_token['user_id']
        user = User.objects.get(id=user_id)
        logger.info(f"[JWT Middleware] Successfully authenticated user: {user.email}")
        return user
    except Exception as e:
        logger.error(f"[JWT Middleware] Authentication failed: {str(e)}")
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections using JWT tokens.
    
    Token can be passed via query parameter: ?token=<jwt_token>
    """
    
    async def __call__(self, scope, receive, send):
        # Only process WebSocket connections
        if scope.get('type') != 'websocket':
            return await super().__call__(scope, receive, send)
        
        path = scope.get('path', '')
        logger.info(f"[JWT Middleware] Processing WebSocket connection to: {path}")
        
        # Get token from query string
        query_string = scope.get('query_string', b'').decode()
        logger.info(f"[JWT Middleware] Query string: {query_string}")
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        try:
            if token:
                logger.info(f"[JWT Middleware] Token found in query string")
                scope['user'] = await get_user_from_token(token)
            else:
                logger.warning(f"[JWT Middleware] No token found, using session auth or anonymous")
                # Try to get user from session (AuthMiddlewareStack handles this)
                # If not set, use AnonymousUser
                if 'user' not in scope:
                    scope['user'] = AnonymousUser()
            
            user = scope.get('user')
            is_auth = user and hasattr(user, 'is_authenticated') and user.is_authenticated
            logger.info(f"[JWT Middleware] User set: {user} (authenticated: {is_auth})")
        except Exception as e:
            logger.error(f"[JWT Middleware] Error during authentication: {str(e)}", exc_info=True)
            # Don't block connection - set anonymous user
            scope['user'] = AnonymousUser()
            logger.info(f"[JWT Middleware] Set anonymous user after error")
        
        try:
            return await super().__call__(scope, receive, send)
        except Exception as e:
            logger.error(f"[JWT Middleware] Error in middleware chain: {str(e)}", exc_info=True)
            raise


def JWTAuthMiddlewareStack(inner):
    """Helper function to wrap URLRouter with JWT auth middleware."""
    return JWTAuthMiddleware(inner)
