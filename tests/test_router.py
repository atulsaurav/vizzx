"""Tests for vizzx.router — the FastAPI router factory."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from vizzx import create_ui_router, mount_static


def _make_app(**kwargs) -> FastAPI:
    """Build a minimal FastAPI app with the VizzX UI router + a stub /api/preloaded."""
    app = FastAPI()
    app.include_router(create_ui_router(**kwargs))
    mount_static(app)

    @app.get("/api/preloaded")
    async def preloaded():
        return JSONResponse(content=None)

    return app


@pytest.fixture
def default_app():
    return _make_app()


@pytest.fixture
def custom_app():
    return _make_app(
        title="Test Viewer",
        upload_accept=".csv,.json",
        upload_label="Drop a data file here",
        api_prefix="/v2",
    )


@pytest.mark.anyio
async def test_index_serves_html(default_app):
    async with AsyncClient(
        transport=ASGITransport(app=default_app), base_url="http://test"
    ) as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "<html" in resp.text


@pytest.mark.anyio
async def test_index_default_config(default_app):
    async with AsyncClient(
        transport=ASGITransport(app=default_app), base_url="http://test"
    ) as client:
        resp = await client.get("/")
    html = resp.text
    assert 'data-api-base=""' in html
    assert 'data-title="Graph Viewer"' in html
    assert 'data-upload-accept=""' in html
    assert 'data-upload-label="Upload a file to analyze"' in html


@pytest.mark.anyio
async def test_index_custom_config(custom_app):
    async with AsyncClient(
        transport=ASGITransport(app=custom_app), base_url="http://test"
    ) as client:
        resp = await client.get("/")
    html = resp.text
    assert 'data-api-base="/v2"' in html
    assert 'data-title="Test Viewer"' in html
    assert 'data-upload-accept=".csv,.json"' in html
    assert 'data-upload-label="Drop a data file here"' in html


@pytest.mark.anyio
async def test_static_assets_served(default_app):
    async with AsyncClient(
        transport=ASGITransport(app=default_app), base_url="http://test"
    ) as client:
        for path in ["/static/app.js", "/static/style.css"]:
            resp = await client.get(path)
            assert resp.status_code == 200, f"Failed to serve {path}"


@pytest.mark.anyio
async def test_html_escaping():
    """Ensure injected config values are HTML-escaped to prevent XSS."""
    app = _make_app(title='<script>alert("xss")</script>')
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/")
    assert "<script>alert" not in resp.text
    assert "&lt;script&gt;" in resp.text
