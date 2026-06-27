"""Security middleware and helpers.

Three layers:
  1. Security headers (CSP, X-Frame-Options, etc.) on every response.
  2. Rate limiting (slowapi) on state-changing routes.
  3. Origin/Referer check on POST routes (lightweight CSRF mitigation).

Upgrade path: when user accounts are introduced, replace the origin check
with full CSRF tokens (e.g. fastapi-csrf-protect).
"""
from __future__ import annotations

import os
from urllib.parse import urlparse

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


# CDNs Tailwind + HTMX are loaded from — must be allowlisted in CSP.
_CSP = "; ".join([
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com",
    "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com",
    "img-src 'self' data: https:",
    "font-src 'self' data:",
    "connect-src 'self'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
])

_DEFAULT_HEADERS = {
    "Content-Security-Policy": _CSP,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=(self)",
    # HSTS is only sent on HTTPS; harmless on plain HTTP responses (browsers ignore).
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for k, v in _DEFAULT_HEADERS.items():
            response.headers.setdefault(k, v)
        return response


def _extra_allowed_hosts() -> set[str]:
    """Extra allowed external origins (preview deploys, partner embeds, etc.)."""
    hosts: set[str] = set()
    site = os.getenv("SITE_URL", "").strip()
    if site:
        hosts.add(urlparse(site).netloc)
    extra = os.getenv("ALLOWED_ORIGINS", "").strip()
    if extra:
        for u in extra.split(","):
            u = u.strip()
            if u:
                hosts.add(urlparse(u).netloc)
    return hosts


def assert_safe_origin(request: Request) -> None:
    """Raise 403 if a POST originates from an unexpected origin.

    Logic:
      - Origin/Referer host must equal the request's own Host header
        (same-origin), OR
      - Origin/Referer host is on the explicit allowlist (ALLOWED_ORIGINS
        env var or SITE_URL).
    Missing Origin AND Referer = blocked.

    Cheap defense against CSRF and arbitrary 3rd-party form posts. Not a
    substitute for proper CSRF tokens if/when user accounts ship.
    """
    if request.method not in {"POST", "PUT", "DELETE", "PATCH"}:
        return

    origin = request.headers.get("origin") or ""
    referer = request.headers.get("referer") or ""

    candidate = ""
    if origin:
        candidate = urlparse(origin).netloc
    elif referer:
        candidate = urlparse(referer).netloc

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing Origin/Referer.",
        )

    request_host = (request.headers.get("host") or "").lower()
    if candidate.lower() == request_host:
        return

    if candidate in _extra_allowed_hosts():
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Origin not allowed.",
    )
