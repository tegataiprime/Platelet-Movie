"""Unit tests for platelet_movie.scraper."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from platelet_movie.config import Config
from platelet_movie.models import Movie
from platelet_movie.scraper import NetflixScraper, _parse_netflix_duration

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(**overrides):
    defaults = dict(
        netflix_email="user@example.com",
        netflix_password="secret",
        headless=True,
        request_delay_s=0.0,  # no sleeping in tests
        page_timeout_ms=5000,
        max_movies=10,
    )
    defaults.update(overrides)
    return Config(**defaults)


def _make_playwright_mocks(mocker):
    """Return (mock_sync_playwright_ctx, mock_page) wired up realistically."""
    mock_page = MagicMock()
    mock_context = MagicMock()
    mock_browser = MagicMock()
    mock_pw = MagicMock()

    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    mock_pw.chromium.launch.return_value = mock_browser

    mock_sync_playwright = mocker.patch("platelet_movie.scraper.sync_playwright")
    mock_sync_playwright.return_value.__enter__.return_value = mock_pw
    mock_sync_playwright.return_value.__exit__.return_value = False

    return mock_pw, mock_browser, mock_page


def _make_link_mock(href: str) -> MagicMock:
    link = MagicMock()
    link.get_attribute.return_value = href
    return link


# ---------------------------------------------------------------------------
# _parse_netflix_duration
# ---------------------------------------------------------------------------


class TestParseNetflixDuration:
    def test_hours_and_minutes(self):
        assert _parse_netflix_duration("2h 18m") == 138

    def test_hours_and_minutes_no_space(self):
        assert _parse_netflix_duration("1h42m") == 102

    def test_minutes_only(self):
        assert _parse_netflix_duration("45m") == 45

    def test_hours_only(self):
        assert _parse_netflix_duration("2h") == 120

    def test_returns_zero_for_empty_string(self):
        assert _parse_netflix_duration("") == 0

    def test_returns_zero_for_unparseable(self):
        assert _parse_netflix_duration("N/A") == 0

    def test_ignores_surrounding_text(self):
        assert _parse_netflix_duration("Runtime: 2h 18m remaining") == 138

    def test_single_minute(self):
        assert _parse_netflix_duration("1m") == 1

    def test_leading_trailing_whitespace(self):
        assert _parse_netflix_duration("  3h 5m  ") == 185


# ---------------------------------------------------------------------------
# NetflixScraper.get_movies – top-level integration (Playwright mocked)
# ---------------------------------------------------------------------------


class TestGetMovies:
    def test_returns_sorted_movies(self, mocker):
        cfg = _make_config()
        scraper = NetflixScraper(cfg)

        # Patch internal helpers so the test is fast and deterministic
        mocker.patch.object(scraper._auth, "login")
        mocker.patch.object(
            scraper,
            "_scrape_movies",
            return_value=[
                Movie(title="Zulu", runtime_minutes=200),
                Movie(title="Alpha", runtime_minutes=148),
            ],
        )
        mock_pw, mock_browser, mock_page = _make_playwright_mocks(mocker)

        movies = scraper.get_movies(min_minutes=135)

        assert movies[0].title == "Alpha"
        assert movies[1].title == "Zulu"

    def test_raises_for_negative_min_minutes(self):
        scraper = NetflixScraper(_make_config())
        with pytest.raises(ValueError, match="non-negative"):
            scraper.get_movies(min_minutes=-1)

    def test_browser_closed_even_on_exception(self, mocker):
        cfg = _make_config()
        scraper = NetflixScraper(cfg)

        mock_pw, mock_browser, mock_page = _make_playwright_mocks(mocker)
        mocker.patch.object(scraper._auth, "login", side_effect=RuntimeError("boom"))

        with pytest.raises(RuntimeError, match="boom"):
            scraper.get_movies()

        mock_browser.close.assert_called_once()

    def test_launches_headless_browser(self, mocker):
        cfg = _make_config(headless=True)
        scraper = NetflixScraper(cfg)

        mock_pw, mock_browser, mock_page = _make_playwright_mocks(mocker)
        mocker.patch.object(scraper._auth, "login")
        mocker.patch.object(scraper, "_scrape_movies", return_value=[])

        scraper.get_movies()

        mock_pw.chromium.launch.assert_called_once_with(headless=True)

    def test_launches_non_headless_browser(self, mocker):
        cfg = _make_config(headless=False)
        scraper = NetflixScraper(cfg)

        mock_pw, mock_browser, mock_page = _make_playwright_mocks(mocker)
        mocker.patch.object(scraper._auth, "login")
        mocker.patch.object(scraper, "_scrape_movies", return_value=[])

        scraper.get_movies()

        mock_pw.chromium.launch.assert_called_once_with(headless=False)

    def test_calls_auth_login(self, mocker):
        cfg = _make_config()
        scraper = NetflixScraper(cfg)

        mock_pw, mock_browser, mock_page = _make_playwright_mocks(mocker)
        login_mock = mocker.patch.object(scraper._auth, "login")
        mocker.patch.object(scraper, "_scrape_movies", return_value=[])

        scraper.get_movies()

        login_mock.assert_called_once_with(mock_page)


# ---------------------------------------------------------------------------
# NetflixScraper._collect_title_urls
# ---------------------------------------------------------------------------


class TestCollectTitleUrls:
    def _scraper(self):
        return NetflixScraper(_make_config())

    def test_returns_absolute_urls(self):
        page = MagicMock()
        page.query_selector_all.return_value = [
            _make_link_mock("/title/12345"),
        ]
        scraper = self._scraper()
        urls = scraper._collect_title_urls(page)
        assert urls == ["https://www.netflix.com/title/12345"]

    def test_deduplicates_urls(self):
        page = MagicMock()
        page.query_selector_all.return_value = [
            _make_link_mock("/title/12345"),
            _make_link_mock("/title/12345"),
            _make_link_mock("/title/12345?trkid=abc"),
        ]
        scraper = self._scraper()
        urls = scraper._collect_title_urls(page)
        assert urls == ["https://www.netflix.com/title/12345"]

    def test_strips_query_string(self):
        page = MagicMock()
        page.query_selector_all.return_value = [
            _make_link_mock("/title/99?someParam=1"),
        ]
        scraper = self._scraper()
        urls = scraper._collect_title_urls(page)
        assert urls == ["https://www.netflix.com/title/99"]

    def test_strips_fragment(self):
        page = MagicMock()
        page.query_selector_all.return_value = [
            _make_link_mock("/title/77#section"),
        ]
        scraper = self._scraper()
        urls = scraper._collect_title_urls(page)
        assert urls == ["https://www.netflix.com/title/77"]

    def test_skips_links_without_title_segment(self):
        page = MagicMock()
        page.query_selector_all.return_value = [
            _make_link_mock("/browse/genre/34399"),
            _make_link_mock("/title/123"),
        ]
        scraper = self._scraper()
        urls = scraper._collect_title_urls(page)
        assert urls == ["https://www.netflix.com/title/123"]

    def test_scrolls_to_load_content(self):
        page = MagicMock()
        page.query_selector_all.return_value = []
        scraper = self._scraper()
        scraper._collect_title_urls(page)
        # Should call evaluate (scroll) 3 times
        assert page.evaluate.call_count == 3

    def test_preserves_insertion_order(self):
        page = MagicMock()
        page.query_selector_all.return_value = [
            _make_link_mock("/title/1"),
            _make_link_mock("/title/2"),
            _make_link_mock("/title/3"),
        ]
        scraper = self._scraper()
        urls = scraper._collect_title_urls(page)
        assert urls == [
            "https://www.netflix.com/title/1",
            "https://www.netflix.com/title/2",
            "https://www.netflix.com/title/3",
        ]


# ---------------------------------------------------------------------------
# NetflixScraper._get_movie_details
# ---------------------------------------------------------------------------


class TestGetMovieDetails:
    def _scraper(self):
        return NetflixScraper(_make_config())

    def _page_with(self, title: str, runtime: str) -> MagicMock:
        page = MagicMock()
        page.query_selector.side_effect = lambda sel: (
            MagicMock(inner_text=MagicMock(return_value=title))
            if sel in ("[data-uia='title']", "h1")
            else MagicMock(inner_text=MagicMock(return_value=runtime))
        )
        return page

    def test_returns_movie_with_parsed_runtime(self):
        page = MagicMock()
        scraper = self._scraper()

        # Wire extract helpers
        with (
            patch.object(NetflixScraper, "_extract_title", return_value="Inception"),
            patch.object(NetflixScraper, "_extract_runtime_text", return_value="2h 28m"),
        ):
            movie = scraper._get_movie_details(page, "https://www.netflix.com/title/123")

        assert movie is not None
        assert movie.title == "Inception"
        assert movie.runtime_minutes == 148

    def test_returns_none_when_no_title(self):
        page = MagicMock()
        scraper = self._scraper()

        with (
            patch.object(NetflixScraper, "_extract_title", return_value=""),
            patch.object(NetflixScraper, "_extract_runtime_text", return_value="2h 28m"),
        ):
            result = scraper._get_movie_details(page, "https://www.netflix.com/title/1")

        assert result is None

    def test_returns_none_when_no_runtime_text(self):
        page = MagicMock()
        scraper = self._scraper()

        with (
            patch.object(NetflixScraper, "_extract_title", return_value="Some Movie"),
            patch.object(NetflixScraper, "_extract_runtime_text", return_value=""),
        ):
            result = scraper._get_movie_details(page, "https://www.netflix.com/title/1")

        assert result is None

    def test_returns_none_when_duration_unparseable(self):
        page = MagicMock()
        scraper = self._scraper()

        with (
            patch.object(NetflixScraper, "_extract_title", return_value="Some Movie"),
            patch.object(NetflixScraper, "_extract_runtime_text", return_value="N/A"),
        ):
            result = scraper._get_movie_details(page, "https://www.netflix.com/title/1")

        assert result is None

    def test_navigates_to_url(self):
        page = MagicMock()
        scraper = self._scraper()
        url = "https://www.netflix.com/title/42"

        with (
            patch.object(NetflixScraper, "_extract_title", return_value=""),
            patch.object(NetflixScraper, "_extract_runtime_text", return_value=""),
        ):
            scraper._get_movie_details(page, url)

        page.goto.assert_called_once_with(url, timeout=scraper._config.page_timeout_ms)


# ---------------------------------------------------------------------------
# NetflixScraper._extract_title
# ---------------------------------------------------------------------------


class TestExtractTitle:
    def test_uses_data_uia_attribute_first(self):
        page = MagicMock()
        el = MagicMock()
        el.inner_text.return_value = "  Inception  "
        # First call ([data-uia='title']) returns the element
        page.query_selector.side_effect = lambda sel: el if sel == "[data-uia='title']" else None

        result = NetflixScraper._extract_title(page)
        assert result == "Inception"

    def test_falls_back_to_h1(self):
        page = MagicMock()
        h1_el = MagicMock()
        h1_el.inner_text.return_value = "Interstellar"

        def selector_side_effect(sel):
            if sel == "[data-uia='title']":
                return None
            if sel == "h1":
                return h1_el
            return None

        page.query_selector.side_effect = selector_side_effect

        result = NetflixScraper._extract_title(page)
        assert result == "Interstellar"

    def test_returns_empty_string_when_no_match(self):
        page = MagicMock()
        page.query_selector.return_value = None
        assert NetflixScraper._extract_title(page) == ""

    def test_skips_element_with_empty_text(self):
        page = MagicMock()
        empty_el = MagicMock()
        empty_el.inner_text.return_value = "   "
        h1_el = MagicMock()
        h1_el.inner_text.return_value = "The Title"

        def selector_side_effect(sel):
            if sel == "[data-uia='title']":
                return empty_el
            if sel == "h1":
                return h1_el
            return None

        page.query_selector.side_effect = selector_side_effect

        result = NetflixScraper._extract_title(page)
        assert result == "The Title"


# ---------------------------------------------------------------------------
# NetflixScraper._extract_runtime_text
# ---------------------------------------------------------------------------


class TestExtractRuntimeText:
    def test_returns_text_from_duration_class(self):
        page = MagicMock()
        el = MagicMock()
        el.inner_text.return_value = "2h 18m"
        page.query_selector.side_effect = lambda sel: el if sel == ".duration" else None

        result = NetflixScraper._extract_runtime_text(page)
        assert result == "2h 18m"

    def test_falls_back_to_body_scan(self):
        page = MagicMock()
        page.query_selector.return_value = None
        page.inner_text.return_value = "Some text 1h 45m more text"

        result = NetflixScraper._extract_runtime_text(page)
        assert "1h 45m" in result

    def test_skips_selector_without_duration_pattern(self):
        page = MagicMock()
        el = MagicMock()
        el.inner_text.return_value = "Some genre info"  # no duration
        body_el = MagicMock()
        body_el.inner_text.return_value = "42m"

        def qs(sel):
            if sel == ".duration":
                return el
            return None

        page.query_selector.side_effect = qs
        page.inner_text.return_value = "42m"

        result = NetflixScraper._extract_runtime_text(page)
        assert result == "42m"

    def test_returns_empty_when_nothing_found(self):
        page = MagicMock()
        page.query_selector.return_value = None
        page.inner_text.return_value = "No duration info here"

        result = NetflixScraper._extract_runtime_text(page)
        assert result == ""


# ---------------------------------------------------------------------------
# NetflixScraper._scrape_movies – filtering and capping
# ---------------------------------------------------------------------------


class TestScrapeMovies:
    def _scraper(self, **cfg_overrides):
        return NetflixScraper(_make_config(**cfg_overrides))

    def test_filters_movies_below_threshold(self, mocker):
        scraper = self._scraper(max_movies=10)
        page = MagicMock()

        mocker.patch.object(
            scraper,
            "_collect_title_urls",
            return_value=["https://www.netflix.com/title/1"],
        )
        mocker.patch.object(
            scraper,
            "_get_movie_details",
            return_value=Movie(title="Short", runtime_minutes=90),
        )

        result = scraper._scrape_movies(page, min_minutes=135)
        assert result == []

    def test_includes_movies_at_threshold(self, mocker):
        scraper = self._scraper(max_movies=10)
        page = MagicMock()

        mocker.patch.object(
            scraper,
            "_collect_title_urls",
            return_value=["https://www.netflix.com/title/1"],
        )
        mocker.patch.object(
            scraper,
            "_get_movie_details",
            return_value=Movie(title="Exact", runtime_minutes=135),
        )

        result = scraper._scrape_movies(page, min_minutes=135)
        assert len(result) == 1

    def test_respects_max_movies_cap(self, mocker):
        scraper = self._scraper(max_movies=2)
        page = MagicMock()

        mocker.patch.object(
            scraper,
            "_collect_title_urls",
            return_value=[f"https://www.netflix.com/title/{i}" for i in range(10)],
        )
        mocker.patch.object(
            scraper,
            "_get_movie_details",
            return_value=Movie(title="Long", runtime_minutes=200),
        )

        result = scraper._scrape_movies(page, min_minutes=135)
        assert len(result) == 2

    def test_skips_failed_title_pages(self, mocker):
        scraper = self._scraper(max_movies=10)
        page = MagicMock()

        mocker.patch.object(
            scraper,
            "_collect_title_urls",
            return_value=["https://www.netflix.com/title/1"],
        )
        mocker.patch.object(
            scraper,
            "_get_movie_details",
            side_effect=RuntimeError("page failed"),
        )

        result = scraper._scrape_movies(page, min_minutes=135)
        assert result == []

    def test_skips_none_movie_details(self, mocker):
        scraper = self._scraper(max_movies=10)
        page = MagicMock()

        mocker.patch.object(
            scraper,
            "_collect_title_urls",
            return_value=["https://www.netflix.com/title/1"],
        )
        mocker.patch.object(scraper, "_get_movie_details", return_value=None)

        result = scraper._scrape_movies(page, min_minutes=135)
        assert result == []


# ---------------------------------------------------------------------------
# NetflixScraper._throttle
# ---------------------------------------------------------------------------


class TestThrottle:
    def test_calls_sleep(self, mocker):
        mock_sleep = mocker.patch("platelet_movie.scraper.time.sleep")
        cfg = _make_config(request_delay_s=1.0)
        scraper = NetflixScraper(cfg)
        scraper._throttle()
        assert mock_sleep.called

    def test_sleep_duration_at_least_request_delay(self, mocker):
        mock_sleep = mocker.patch("platelet_movie.scraper.time.sleep")
        cfg = _make_config(request_delay_s=2.0)
        scraper = NetflixScraper(cfg)
        scraper._throttle()
        sleep_duration = mock_sleep.call_args[0][0]
        assert sleep_duration >= 2.0

    def test_sleep_duration_no_more_than_150_percent_of_delay(self, mocker):
        mock_sleep = mocker.patch("platelet_movie.scraper.time.sleep")
        cfg = _make_config(request_delay_s=2.0)
        scraper = NetflixScraper(cfg)
        scraper._throttle()
        sleep_duration = mock_sleep.call_args[0][0]
        assert sleep_duration <= 3.0  # 2.0 + 50% jitter = 3.0 max
