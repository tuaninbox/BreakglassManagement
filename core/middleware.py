from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.audit_logger import log_action
from deps.auth import get_current_user_optional  


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user = await get_current_user_optional(request)

        # Pre-request log
        log_action(
            user=user,
            action="http_request",
            details=f"{request.method} {request.url.path}",
            request=request,
            category="navigation"
        )

        response: Response = await call_next(request)

        # Post-request log
        log_action(
            user=user,
            action="http_response",
            details=f"Status {response.status_code} for {request.method} {request.url.path}",
            request=request,
            category="navigation"
        )

        return response

