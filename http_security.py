"""HTTP middleware for Render: public health check, API key on MCP routes."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

import config

_PUBLIC_PATHS = frozenset({"/health"})


def _extract_api_key(request: Request) -> str | None:
    """Read API key from X-API-Key or Authorization Bearer header."""
    header = request.headers.get("x-api-key", "").strip()
    if header:
        return header
    auth = request.headers.get("authorization", "").strip()
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Reject HTTP requests when MCP_API_KEY is set and the client did not send it."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Allow /health; require API key for everything else when configured."""
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)
        expected = config.mcp_api_key()
        if not expected:
            return await call_next(request)
        provided = _extract_api_key(request)
        if provided != expected:
            return JSONResponse(
                {"error": "unauthorized", "hint": "Send X-API-Key or Authorization: Bearer"},
                status_code=401,
            )
        return await call_next(request)


def http_middleware_stack() -> list:
    """Return Starlette middleware list for streamable-http deploys."""
    from starlette.middleware import Middleware

    return [Middleware(ApiKeyMiddleware)]
