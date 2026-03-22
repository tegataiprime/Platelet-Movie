"""Netflix scraper – discovers movies using a Playwright-controlled browser.

Rate-limiting and anti-lockout safeguards
-----------------------------------------
* A configurable delay (default 2 s, plus random jitter up to 50 % extra) is
  applied between every page load so that Netflix cannot distinguish the scraper
  from a slow human reader.
* The total number of movie detail pages visited per session is capped by
  ``Config.max_movies`` (default 100) to avoid triggering volumetric
  rate-limiting or temporary account suspension.
* The browser presents a realistic user-agent string and a standard desktop
  viewport so that Netflix's bot-detection heuristics see a normal browser.
* Any page that fails to load (timeout, unexpected redirect, etc.) is silently
  skipped rather than retried aggressively.
"""

from __future__ import annotations

import random
import re
import time
from typing import TYPE_CHECKING

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from platelet_movie.auth import NetflixAuth
from platelet_movie.config import Config
from platelet_movie.models import Movie

if TYPE_CHECKING:
    from playwright.sync_api import Page

# -----------------------------------------------------------------------
# Netflix URLs
# -----------------------------------------------------------------------

_NETFLIX_MOVIES_URL = "https://www.netflix.com/browse/genre/34399"

# -----------------------------------------------------------------------
# Browser identity – mimic a real desktop Chrome session
# -----------------------------------------------------------------------

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)

# -----------------------------------------------------------------------
# Duration parsing – Netflix shows runtimes like "2h 18m", "45m", "2h"
# -----------------------------------------------------------------------

# Matches "2h 18m", "1h42m", "45m", "2h" anywhere in a string
_DURATION_PATTERN = re.compile(r"(?:(\d+)h\s*(\d+)m)|(?:(\d+)h\b)|(?:(\d+)m\b)")

# CSS selectors tried in order when looking for runtime on a title page
_DURATION_SELECTORS = (
    ".duration",
    "[data-uia='duration']",
    ".title-info-metadata-item",
    ".supplementalMessage",
)

# CSS selectors tried in order when looking for the movie title
_TITLE_SELECTORS = (
    "[data-uia='title']",
    "h1",
)


class NetflixScraper:
    """Playwright-based scraper that discovers Netflix movies by runtime.

    Uses a real Chromium browser session (via Playwright) to authenticate with
    Netflix and browse the movie catalog, collecting titles and runtimes.

    Rate-limiting is enforced between every page load to avoid triggering
    Netflix's bot-detection systems or locking the subscriber account.
    """

    def __init__(self, config: Config, auth: NetflixAuth | None = None) -> None:
        self._config = config
        self._auth = auth or NetflixAuth(config)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_movies(self, min_minutes: int = 135) -> list[Movie]:
        """Return movies with runtime >= *min_minutes*, sorted ascending.

        Launches a Chromium browser, logs in to Netflix, browses the movies
        catalog, and inspects individual title pages to determine runtimes.

        Args:
            min_minutes: Minimum runtime in minutes (inclusive). Defaults to 135.

        Returns:
            Sorted list of :class:`~platelet_movie.models.Movie` instances.

        Raises:
            ValueError: If *min_minutes* is negative.
            playwright.sync_api.TimeoutError: If login times out.
        """
        if min_minutes < 0:
            raise ValueError("min_minutes must be a non-negative integer.")

        movies: list[Movie] = []
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self._config.headless)
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent=_USER_AGENT,
            )
            page = context.new_page()
            try:
                self._auth.login(page)
                movies = self._scrape_movies(page, min_minutes)
            finally:
                browser.close()

        return sorted(movies)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _scrape_movies(self, page: "Page", min_minutes: int) -> list[Movie]:
        """Navigate the Netflix movies browse page and collect matching movies."""
        page.goto(_NETFLIX_MOVIES_URL, timeout=self._config.page_timeout_ms)
        self._throttle()

        title_urls = self._collect_title_urls(page)
        movies: list[Movie] = []

        for url in title_urls[: self._config.max_movies]:
            try:
                movie = self._get_movie_details(page, url)
            except (PlaywrightTimeoutError, Exception):  # noqa: BLE001
                # Skip any title that cannot be loaded; do not retry aggressively.
                continue

            if movie is not None and movie.runtime_minutes >= min_minutes:
                movies.append(movie)

            self._throttle()

        return movies

    def _collect_title_urls(self, page: "Page") -> list[str]:
        """Return a deduplicated list of ``/title/`` URLs visible on the page.

        Scrolls down a few viewport-heights to trigger lazy-loaded carousels
        before harvesting the links.
        """
        # Scroll to reveal lazy-loaded content before harvesting links
        for _ in range(3):
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            self._throttle()

        links = page.query_selector_all("a[href*='/title/']")
        seen: set[str] = set()
        urls: list[str] = []
        for link in links:
            href = link.get_attribute("href") or ""
            # Normalise to an absolute URL
            if href.startswith("/"):
                href = f"https://www.netflix.com{href}"
            # Strip query strings / fragments so duplicates collapse
            href = href.split("?")[0].split("#")[0]
            if href not in seen and "/title/" in href:
                seen.add(href)
                urls.append(href)
        return urls

    def _get_movie_details(self, page: "Page", url: str) -> Movie | None:
        """Navigate to a Netflix title page and return a :class:`Movie` or ``None``."""
        page.goto(url, timeout=self._config.page_timeout_ms)
        page.wait_for_load_state("domcontentloaded", timeout=self._config.page_timeout_ms)

        title = self._extract_title(page)
        runtime_text = self._extract_runtime_text(page)

        if not title or not runtime_text:
            return None

        runtime = _parse_netflix_duration(runtime_text)
        if runtime == 0:
            return None

        return Movie(title=title, runtime_minutes=runtime)

    @staticmethod
    def _extract_title(page: "Page") -> str:
        """Extract the movie title from the current Netflix page."""
        for selector in _TITLE_SELECTORS:
            el = page.query_selector(selector)
            if el:
                text = el.inner_text().strip()
                if text:
                    return text
        return ""

    @staticmethod
    def _extract_runtime_text(page: "Page") -> str:
        """Extract the raw runtime string from the current Netflix title page.

        Tries dedicated duration selectors first, then falls back to scanning
        the entire page body with a regex.
        """
        for selector in _DURATION_SELECTORS:
            el = page.query_selector(selector)
            if el:
                text = el.inner_text().strip()
                if _DURATION_PATTERN.search(text):
                    return text

        # Last resort: find the first duration-like pattern anywhere on the page
        body_text = page.inner_text("body")
        match = _DURATION_PATTERN.search(body_text)
        if match:
            return match.group(0)

        return ""

    def _throttle(self) -> None:
        """Sleep for ``request_delay_s`` plus random jitter (up to 50 % extra).

        The jitter prevents Netflix from seeing a perfectly regular request
        cadence, which would be a strong bot signal.
        """
        jitter = random.uniform(0.0, 0.5 * self._config.request_delay_s)
        time.sleep(self._config.request_delay_s + jitter)


# ---------------------------------------------------------------------------
# Duration parsing utility
# ---------------------------------------------------------------------------


def _parse_netflix_duration(text: str) -> int:
    """Parse a Netflix duration string into total minutes.

    Handles the following formats (case-insensitive):

    * ``"2h 18m"`` → 138
    * ``"1h42m"`` → 102
    * ``"45m"`` → 45
    * ``"2h"`` → 120

    Returns ``0`` if no recognisable pattern is found.
    """
    text = text.strip()

    # "Xh Ym" or "XhYm"
    m = re.search(r"(\d+)h\s*(\d+)m", text)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))

    # "Xh" alone
    m = re.search(r"(\d+)h\b", text)
    if m:
        return int(m.group(1)) * 60

    # "Xm" alone
    m = re.search(r"(\d+)m\b", text)
    if m:
        return int(m.group(1))

    return 0
