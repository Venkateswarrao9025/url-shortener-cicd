"""Tests for the URL-shortener API.

These run in CI on every push. If any test fails, the pipeline stops and
nothing gets deployed -- that's the whole point of the "test gate".
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_shorten_returns_code():
    response = client.post("/shorten", json={"url": "https://example.com"})
    assert response.status_code == 200
    body = response.json()
    assert "code" in body
    assert body["original_url"] == "https://example.com/"


def test_shorten_rejects_invalid_url():
    response = client.post("/shorten", json={"url": "not-a-url"})
    assert response.status_code == 422  # validation error


def test_redirect_works():
    # Create a short code, then follow it.
    code = client.post("/shorten", json={"url": "https://example.org"}).json()["code"]
    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.org/"


def test_redirect_unknown_code_is_404():
    response = client.get("/does-not-exist", follow_redirects=False)
    assert response.status_code == 404


def test_list_links_includes_created_link():
    code = client.post("/shorten", json={"url": "https://python.org"}).json()["code"]
    links = client.get("/api/links").json()
    assert links[code] == "https://python.org/"
