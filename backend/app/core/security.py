"""Input validation and URL safety helpers."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

from app.core.config import settings


class SecurityValidationError(ValueError):
    pass


def validate_eda_recipe_url(url: str) -> str:
    parsed = urlparse((url or "").strip())
    if parsed.scheme != "https":
        raise SecurityValidationError("Allowed only https:// URLs.")
    if parsed.scheme in {"file", "ftp"}:
        raise SecurityValidationError("file:// and ftp:// URLs are forbidden.")
    if parsed.username or parsed.password:
        raise SecurityValidationError("URLs with embedded credentials are forbidden.")

    host = (parsed.hostname or "").lower()
    if not host:
        raise SecurityValidationError("URL host is required.")
    if host in {"localhost", "127.0.0.1", "::1"}:
        raise SecurityValidationError("localhost URLs are forbidden.")
    _reject_private_ip(host)
    if host != "eda.rambler.ru":
        raise SecurityValidationError("Only https://eda.rambler.ru/recepty/... pages are allowed.")
    if not parsed.path.startswith("/recepty"):
        raise SecurityValidationError("Only eda.rambler.ru recipe pages under /recepty are allowed.")
    return parsed.geturl()


def validate_html_payload(html: str) -> None:
    if html is None or not html.strip():
        raise SecurityValidationError("HTML payload must not be empty.")
    if "<" not in html:
        raise SecurityValidationError("HTML payload must contain markup.")
    validate_html_size(html)


def validate_html_size(html: str | bytes) -> None:
    size = len(html if isinstance(html, bytes) else html.encode("utf-8"))
    if size > settings.max_html_size_bytes:
        raise SecurityValidationError(
            f"HTML payload is too large: {size} bytes, limit is {settings.max_html_size_bytes} bytes."
        )


def _reject_private_ip(host: str) -> None:
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
        raise SecurityValidationError("Private, local and reserved IP addresses are forbidden.")

