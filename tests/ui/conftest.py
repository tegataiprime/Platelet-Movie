"""Shared fixtures for Playwright UI tests.

These tests exercise the static site in `site/` in a real browser (via
Playwright) to catch regressions that pure unit tests cannot, such as CSS
rules that silently override JavaScript-driven visibility toggles.

Run with: `poe install-browsers` (once) then `poe test-ui`.
"""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

SITE_DIR = Path(__file__).parent.parent.parent / "site"

# A minimal, deterministic movie payload used to stub network responses for
# data-{region}.json so tests don't depend on (or mutate) the real,
# generated site data files.
MOCK_SITE_DATA = {
    "generated_at": "2026-01-01T00:00:00Z",
    "commentary": "Dear Reader, what a delightful selection of films.",
    "movies": [
        {
            "tmdb_id": 1,
            "title": "Alpha Film",
            "runtime_minutes": 90,
            "year": 2020,
            "genres": ["Drama"],
            "rating": 7.1,
            "vote_average": 7.1,
            "certification": "PG-13",
            "description": "A short film.",
        },
        {
            "tmdb_id": 2,
            "title": "Zulu Film",
            "runtime_minutes": 150,
            "year": 2021,
            "genres": ["Action"],
            "rating": 8.2,
            "vote_average": 8.2,
            "certification": "R",
            "description": "A longer film.",
        },
    ],
}


@pytest.fixture(scope="session")
def site_base_url() -> Iterator[str]:
    """Serve the site/ directory over HTTP for the duration of the test session."""
    handler = partial(SimpleHTTPRequestHandler, directory=str(SITE_DIR))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.fixture
def site_page(page, site_base_url):
    """A Playwright page navigated to the site's index page with mocked movie data.

    Network requests for data-*.json are intercepted and fulfilled with
    MOCK_SITE_DATA so tests are deterministic and don't depend on (or
    accidentally mutate) the real generated site data files.
    """

    def _fulfill_mock_data(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(MOCK_SITE_DATA),
        )

    page.route("**/data-*.json*", _fulfill_mock_data)
    page.goto(f"{site_base_url}/index.html")
    page.wait_for_selector("#runtime-format-toggle")
    return page
