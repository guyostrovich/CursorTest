"""openFDA client tests. Live calls are faked so nothing touches the network."""

from dataclasses import replace

import httpx
import pytest
from fastapi import HTTPException

from app.config import settings
from app.openfda import search_510k, search_recalls


def _live(monkeypatch, **changes):
    monkeypatch.setattr(
        "app.openfda.settings",
        replace(
            settings,
            openfda_mode="live",
            openfda_base_url="https://fda.example",
            openfda_timeout=3.5,
            **changes,
        ),
    )


class _Response:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = {} if payload is None else payload

    def json(self):
        return self._payload


def test_live_510k_sends_every_word_and_the_api_key(monkeypatch):
    captured = {}

    def fake_get(url, params, timeout):
        captured.update(url=url, params=params, timeout=timeout)
        return _Response(200, {"results": [{"k_number": "K1"}]})

    monkeypatch.setattr("app.openfda.httpx.get", fake_get)
    _live(monkeypatch, openfda_api_key="secret")

    assert search_510k("pace maker") == [{"k_number": "K1"}]
    assert captured["url"] == "https://fda.example/device/510k.json"
    assert captured["params"]["search"] == "device_name:pace AND device_name:maker"
    assert captured["params"]["api_key"] == "secret"
    assert captured["params"]["limit"] == 100
    assert captured["timeout"] == 3.5


def test_live_recall_with_blank_query_and_no_key(monkeypatch):
    captured = {}

    def fake_get(url, params, timeout):
        captured["url"] = url
        captured["params"] = params
        return _Response(200, {})

    monkeypatch.setattr("app.openfda.httpx.get", fake_get)
    _live(monkeypatch, openfda_api_key="")

    assert search_recalls("   ") == []
    assert captured["url"] == "https://fda.example/device/recall.json"
    assert "search" not in captured["params"]
    assert "api_key" not in captured["params"]


def test_live_404_means_no_matches(monkeypatch):
    monkeypatch.setattr("app.openfda.httpx.get", lambda url, params, timeout: _Response(404))
    _live(monkeypatch, openfda_api_key="")
    assert search_510k("nothing") == []


def test_live_403_is_a_bad_gateway(monkeypatch):
    monkeypatch.setattr("app.openfda.httpx.get", lambda url, params, timeout: _Response(403))
    _live(monkeypatch, openfda_api_key="bad")
    with pytest.raises(HTTPException) as caught:
        search_510k("x")
    assert caught.value.status_code == 502
    assert "OPENFDA_API_KEY" in caught.value.detail


def test_live_other_status_is_a_bad_gateway(monkeypatch):
    monkeypatch.setattr("app.openfda.httpx.get", lambda url, params, timeout: _Response(500))
    _live(monkeypatch, openfda_api_key="")
    with pytest.raises(HTTPException) as caught:
        search_recalls("x")
    assert caught.value.status_code == 502
    assert "500" in caught.value.detail


def test_live_timeout_is_a_gateway_timeout(monkeypatch):
    def fake_get(url, params, timeout):
        raise httpx.TimeoutException("slow")

    monkeypatch.setattr("app.openfda.httpx.get", fake_get)
    _live(monkeypatch, openfda_api_key="")
    with pytest.raises(HTTPException) as caught:
        search_510k("x")
    assert caught.value.status_code == 504


def test_live_network_error_is_a_bad_gateway(monkeypatch):
    def fake_get(url, params, timeout):
        raise httpx.ConnectError("down")

    monkeypatch.setattr("app.openfda.httpx.get", fake_get)
    _live(monkeypatch, openfda_api_key="")
    with pytest.raises(HTTPException) as caught:
        search_recalls("x")
    assert caught.value.status_code == 502
    assert "Could not reach openFDA" in caught.value.detail
