from __future__ import annotations

from typing import TYPE_CHECKING

from slowapi import Limiter

from app.config.settings import settings

if TYPE_CHECKING:
    from starlette.requests import Request


def get_rate_limit_key(request: Request) -> str:
    if settings.IS_BEHIND_PROXY:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

    if request.client:
        return request.client.host

    return "unknown"


limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=[settings.API_RATE_LIMIT_DEFAULT],
)
