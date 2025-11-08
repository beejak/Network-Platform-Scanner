"""
Custom Middleware for the FastAPI Application.
"""
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from platform_core.authentication import decode_access_token

logger = logging.getLogger(__name__)

class AuthMiddleware:
    """
    Authentication middleware to validate JWT tokens using the pure ASGI pattern.
    """
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        if request.url.path == "/health" or request.url.path.startswith("/docs"):
            await self.app(scope, receive, send)
            return

        logger.debug(f"AuthMiddleware: Processing request to {request.url.path}")
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning("AuthMiddleware: Authorization header missing")
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header missing"},
            )
            await response(scope, receive, send)
            return

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
        except ValueError:
            logger.warning("AuthMiddleware: Invalid Authorization header format")
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid Authorization header format"},
            )
            await response(scope, receive, send)
            return

        token_data = decode_access_token(token)
        if not token_data:
            logger.warning("AuthMiddleware: Invalid or expired token")
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
            )
            await response(scope, receive, send)
            return

        # Attach user and tenant info to the request scope
        scope["state"] = {
            "user_id": token_data.user_id,
            "tenant_id": token_data.tenant_id,
        }
        logger.debug(f"AuthMiddleware: Token valid. User: {token_data.user_id}, Tenant: {token_data.tenant_id}")

        await self.app(scope, receive, send)
