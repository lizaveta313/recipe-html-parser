def create_report(client, fixture_html) -> dict:
    response = client.post(
        "/api/parse/html",
        json={"html": fixture_html("eda_recipe_valid.html"), "source_name": "fixture valid"},
    )
    assert response.status_code == 200
    return response.json()


def test_get_reports_returns_list(client, fixture_html) -> None:
    create_report(client, fixture_html)
    response = client.get("/api/reports")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_report_by_id(client, fixture_html) -> None:
    report = create_report(client, fixture_html)
    response = client.get(f"/api/reports/{report['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == report["id"]


def test_delete_report(client, fixture_html) -> None:
    report = create_report(client, fixture_html)
    response = client.delete(f"/api/reports/{report['id']}")
    assert response.status_code == 200
    assert response.json()["deleted"] is True
    assert client.get(f"/api/reports/{report['id']}").status_code == 404


def test_missing_report_returns_404(client) -> None:
    response = client.get("/api/reports/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404

