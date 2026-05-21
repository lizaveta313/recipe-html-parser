from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx


def test_post_parse_html_returns_full_report(client, fixture_html) -> None:
    response = client.post(
        "/api/parse/html",
        json={"html": fixture_html("eda_recipe_valid.html"), "source_name": "fixture valid"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["recipe"]["title"] == "Паста с томатами и базиликом"
    assert data["html_analysis"]["tokens_count"] > 0
    assert data["dom_tree_preview"]["tag"] == "document"
    assert data["tokens_preview"]


def test_post_parse_html_saves_report(client, fixture_html) -> None:
    created = client.post(
        "/api/parse/html",
        json={"html": fixture_html("eda_recipe_valid.html"), "source_name": "fixture valid"},
    ).json()
    reports = client.get("/api/reports").json()
    assert len(reports) == 1
    assert reports[0]["id"] == created["id"]


def test_post_parse_url_uses_mocked_httpx(client, fixture_html) -> None:
    mocked_get = AsyncMock(
        return_value=httpx.Response(
            200,
            text=fixture_html("eda_recipe_valid.html"),
            request=httpx.Request("GET", "https://eda.rambler.ru/recepty/pasta/pasta-s-tomatami-i-bazilikom-12345"),
        )
    )
    with patch.object(httpx.AsyncClient, "get", mocked_get):
        response = client.post(
            "/api/parse/url",
            json={"url": "https://eda.rambler.ru/recepty/pasta/pasta-s-tomatami-i-bazilikom-12345"},
        )
    assert response.status_code == 200
    assert response.json()["source_type"] == "url"
    mocked_get.assert_awaited_once()


def test_invalid_url_returns_error(client) -> None:
    response = client.post("/api/parse/url", json={"url": "ftp://eda.rambler.ru/recepty/x"})
    assert response.status_code in {400, 422}


def test_non_eda_recipe_url_is_forbidden(client) -> None:
    response = client.post("/api/parse/url", json={"url": "https://example.com/recepty/x"})
    assert response.status_code == 400


def test_empty_html_returns_error(client) -> None:
    response = client.post("/api/parse/html", json={"html": "", "source_name": "empty"})
    assert response.status_code in {400, 422}


def test_broken_html_does_not_break_application(client, fixture_html) -> None:
    response = client.post(
        "/api/parse/html",
        json={"html": fixture_html("broken_html.html"), "source_name": "broken"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["html_analysis"]["errors_count"] > 0
    assert data["errors"]
