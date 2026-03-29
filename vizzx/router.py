"""
FastAPI router factory for the VizzX interactive DAG visualization frontend.

Usage::

    from fastapi import FastAPI
    from vizzx import create_ui_router, mount_static

    app = FastAPI()
    app.include_router(create_ui_router(
        title="My Graph Viewer",
        upload_accept=".zip,.json",
        upload_label="Upload a file to analyze",
    ))
    mount_static(app)

    # Then register your own /api/analyze and/or /api/preloaded endpoints
    # that return JSON in the shape: {nodes, edges, modules}
"""
from __future__ import annotations

import html as html_mod
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

STATIC_DIR = Path(__file__).parent / "static"


def create_ui_router(
    *,
    api_prefix: str = "",
    title: str = "Graph Viewer",
    upload_accept: str = "",
    upload_label: str = "Upload a file to analyze",
) -> APIRouter:
    """Create an APIRouter that serves the VizzX interactive frontend.

    Parameters
    ----------
    api_prefix:
        URL prefix prepended to ``/api/analyze`` and ``/api/preloaded``
        fetch calls in the frontend JS.  Leave empty if the API endpoints
        are mounted at the same origin root.
    title:
        Application title shown in the browser tab and page header.
    upload_accept:
        Comma-separated file extensions the upload input should accept
        (e.g. ``".zip,.tar.gz"``).  Empty string means accept any file.
    upload_label:
        Text shown in the upload drop-zone area.
    """
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    async def index():
        raw_html = (STATIC_DIR / "index.html").read_text()
        attrs = (
            f'data-api-base="{html_mod.escape(api_prefix)}" '
            f'data-title="{html_mod.escape(title)}" '
            f'data-upload-accept="{html_mod.escape(upload_accept)}" '
            f'data-upload-label="{html_mod.escape(upload_label)}"'
        )
        injected = raw_html.replace("<body>", f"<body {attrs}>", 1)
        return HTMLResponse(content=injected)

    return router


def mount_static(app: FastAPI) -> None:
    """Mount VizzX static assets (JS, CSS, vendor libs) at ``/static``."""
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="vizzx-static")