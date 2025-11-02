import uuid
from typing import Awaitable, Callable

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class TenantIsolationMiddleware(BaseHTTPMiddleware):  # type: ignore
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Extract tenant_id from JWT or header
        tenant_id_str = request.headers.get("X-Tenant-ID")

        if not tenant_id_str and request.url.path.startswith("/api/"):
            raise HTTPException(status_code=401, detail="Tenant ID required")

        if tenant_id_str:
            try:
                tenant_id = uuid.UUID(tenant_id_str)
                request.state.tenant_id = tenant_id
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid Tenant ID format")

        response = await call_next(request)
        return response
