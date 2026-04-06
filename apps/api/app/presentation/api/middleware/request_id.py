from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response


class RequestIdMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Any,
        max_length: int = 100,
        trust_proxy: bool = True,
    ) -> None:
        super().__init__(app)
        self.max_length = max_length
        self.trust_proxy = trust_proxy

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        client_request_id = request.headers.get("X-Request-ID")

        if client_request_id and self._is_valid_request_id(client_request_id):
            request_id = client_request_id
        else:
            request_id = str(uuid.uuid7())

        request.state.request_id = request_id
        client_ip = self._get_client_ip(request)

        with logger.contextualize(request_id=request_id, client_ip=client_ip):
            response = await call_next(request)

        response.headers["X-Request-ID"] = request_id
        return response

    def _is_valid_request_id(self, request_id: str) -> bool:
        return (
            bool(request_id)
            and not request_id.isspace()
            and len(request_id) <= self.max_length
            and request_id.replace("-", "").isalnum()
        )

    def _get_client_ip(self, request: Request) -> str:
        if self.trust_proxy:
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()

            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                return real_ip.strip()

        return request.client.host if request.client else "unknown"
