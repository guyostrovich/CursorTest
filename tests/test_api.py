"""API tests. They read local data and saved fixtures only; no network is involved."""

from fastapi.testclient import TestClient

from app.main import app
from app.models import Update

client = TestClient(app)


def test_health_reports_fixture_mode():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "fixture"}


def test_version_reports_the_app_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "1.1.0"}


def test_products_list_and_detail():
    items = client.get("/products").json()
    assert len(items) == 6
    assert all(item["product_codes"] for item in items)
    assert all(len(code) == 3 and code.isupper() for item in items for code in item["product_codes"])
    assert client.get("/products/pulse-dr").json()["name"] == "Acme Pulse DR"
    assert client.get("/products/does-not-exist").status_code == 404


def test_updates_filter_by_jurisdiction_and_tag():
    fda = client.get("/updates", params={"jurisdiction": "FDA"}).json()
    assert len(fda) == 4
    assert all(u["jurisdiction"] == "FDA" for u in fda)
    ai = client.get("/updates", params={"tag": "ai"}).json()
    assert len(ai) == 3
    assert all("ai" in u["tags"] for u in ai)


def test_updates_without_filters_are_newest_first():
    items = client.get("/updates").json()
    dates = [item["date"] for item in items]
    assert len(items) == 8
    assert dates == sorted(dates, reverse=True)


def test_updates_since_drops_older_updates():
    items = client.get("/updates", params={"since": "2025-01-01"}).json()
    assert len(items) == 7
    assert all(u["date"] >= "2025-01-01" for u in items)
    assert "fda-udi-requirements" not in [u["id"] for u in items]


def test_update_date_without_dashes_is_accepted(monkeypatch):
    monkeypatch.setattr(
        "app.portfolio.load_updates",
        lambda: [_update(date="20250301")],
    )
    kept = client.get("/updates", params={"since": "2025-03-01"}).json()
    dropped = client.get("/updates", params={"since": "2025-03-02"}).json()
    assert [item["id"] for item in kept] == ["plain-date"]
    assert dropped == []


def test_unreadable_update_date_returns_500(monkeypatch):
    monkeypatch.setattr(
        "app.portfolio.load_updates",
        lambda: [_update(date="not-a-date")],
    )
    response = client.get("/updates", params={"since": "2020-01-01"})
    assert response.status_code == 500
    assert "not-a-date" in response.json()["detail"]


def test_clearances_query_and_limit():
    results = client.get("/clearances", params={"query": "pacemaker", "limit": 3}).json()
    assert len(results) == 3
    assert all("pacemaker" in r["device_name"].lower() for r in results)


def test_clearances_blank_query_returns_saved_records():
    results = client.get("/clearances", params={"query": "   ", "limit": 100}).json()
    assert len(results) == 33


def test_recalls_since_keeps_only_newer_recalls():
    params = {"query": "pacemaker", "since": "2017-01-01", "limit": 50}
    results = client.get("/recalls", params=params).json()
    assert len(results) == 6
    assert all(r["event_date_initiated"] >= "2017-01-01" for r in results)
    assert all(r["product_res_number"].startswith("Z-") for r in results)


def test_recalls_without_since_are_not_date_filtered():
    results = client.get("/recalls", params={"query": "pacemaker", "limit": 50}).json()
    assert len(results) == 9


def test_recalls_skip_missing_and_invalid_dates(monkeypatch):
    monkeypatch.setattr(
        "app.openfda.search_recalls",
        lambda query: [
            {"product_res_number": "Z-KEEP", "event_date_initiated": "2024-01-01"},
            {"product_res_number": "Z-OLD", "event_date_initiated": "2020-01-01"},
            {"product_res_number": "Z-NONE"},
            {"product_res_number": "Z-EMPTY", "event_date_initiated": ""},
            {"product_res_number": "Z-BAD", "event_date_initiated": "yesterday"},
        ],
    )
    results = client.get("/recalls", params={"since": "2024-01-01", "limit": 50}).json()
    assert [item["product_res_number"] for item in results] == ["Z-KEEP"]


def _update(date: str) -> Update:
    return Update(
        id="plain-date",
        title="Plain",
        date=date,
        jurisdiction="EU",
        tags=[],
        source_url="https://example.test",
        body="Body",
    )
