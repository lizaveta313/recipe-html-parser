"""HTTP loading service for eda.rambler.ru pages."""

from __future__ import annotations

import logging

import httpx

from app.core.config import settings
from app.core.security import validate_eda_recipe_url, validate_html_size

logger = logging.getLogger(__name__)


class HtmlFetchError(RuntimeError):
    pass


class HtmlFetchService:
    USER_AGENT = "RecipeHTMLParser/1.0 educational-parser (+https://eda.rambler.ru/recepty)"

    async def fetch(self, url: str) -> str:
        safe_url = validate_eda_recipe_url(url)
        headers = {"User-Agent": self.USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
        timeout = httpx.Timeout(settings.http_timeout_seconds)
        try:
            async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
                response = await client.get(safe_url)
                validate_eda_recipe_url(str(response.url))
                response.raise_for_status()
                validate_html_size(response.content)
                return response.text
        except httpx.TimeoutException as exc:
            logger.warning("HTML fetch timeout for %s", safe_url)
            raise HtmlFetchError("HTML request timed out.") from exc
        except httpx.HTTPStatusError as exc:
            logger.warning("HTML fetch HTTP error for %s: %s", safe_url, exc)
            raise HtmlFetchError(f"Remote server returned HTTP {exc.response.status_code}.") from exc
        except httpx.RequestError as exc:
            logger.warning("HTML fetch network error for %s: %s", safe_url, exc)
            raise HtmlFetchError("Network error while loading HTML.") from exc

