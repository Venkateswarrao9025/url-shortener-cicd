"""A minimal URL-shortener API built with FastAPI.

Endpoints:
    GET  /health          -> liveness check (used by deploys/monitoring)
    POST /shorten         -> create a short code for a long URL
    GET  /{code}          -> redirect to the original URL
    GET  /api/links       -> list every stored mapping
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

from app.storage import URLStore

app = FastAPI(title="URL Shortener", version="1.0.0")
store = URLStore()


class ShortenRequest(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    original_url: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/shorten", response_model=ShortenResponse)
def shorten(request: ShortenRequest) -> ShortenResponse:
    url = str(request.url)
    code = store.add(url)
    return ShortenResponse(
        code=code,
        short_url=f"/{code}",
        original_url=url,
    )


@app.get("/api/links")
def list_links() -> dict[str, str]:
    return store.all()


@app.get("/{code}")
def redirect(code: str) -> RedirectResponse:
    url = store.get(code)
    if url is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    return RedirectResponse(url)
