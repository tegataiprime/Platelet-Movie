"""Unit tests for platelet_movie.auth."""

from unittest.mock import MagicMock

from platelet_movie.auth import _NETFLIX_LOGIN_URL, _POST_LOGIN_URL_PATTERN, NetflixAuth
from platelet_movie.config import Config


def _make_config(**kwargs):
    defaults = {
        "netflix_email": "user@example.com",
        "netflix_password": "secret",
        "page_timeout_ms": 5000,
        "request_delay_s": 0,
    }
    defaults.update(kwargs)
    return Config(**defaults)


def _make_page_mock():
    """Return a MagicMock that behaves like a Playwright Page."""
    return MagicMock()


class TestNetflixAuth:
    def test_stores_config(self):
        cfg = _make_config()
        auth = NetflixAuth(cfg)
        assert auth._config is cfg

    def test_login_navigates_to_login_url(self):
        cfg = _make_config()
        auth = NetflixAuth(cfg)
        page = _make_page_mock()

        auth.login(page)

        page.goto.assert_called_once_with(_NETFLIX_LOGIN_URL, timeout=cfg.page_timeout_ms)

    def test_login_fills_email(self):
        cfg = _make_config(netflix_email="me@example.com")
        auth = NetflixAuth(cfg)
        page = _make_page_mock()

        auth.login(page)

        # Find the fill call for the email selector
        fill_calls = {call.args[0]: call.args[1] for call in page.fill.call_args_list}
        assert fill_calls.get("[data-uia='login-field']") == "me@example.com"

    def test_login_fills_password(self):
        cfg = _make_config(netflix_password="mypassword")
        auth = NetflixAuth(cfg)
        page = _make_page_mock()

        auth.login(page)

        fill_calls = {call.args[0]: call.args[1] for call in page.fill.call_args_list}
        assert fill_calls.get("[data-uia='password-field']") == "mypassword"

    def test_login_clicks_submit(self):
        cfg = _make_config()
        auth = NetflixAuth(cfg)
        page = _make_page_mock()

        auth.login(page)

        page.click.assert_called_once_with("[data-uia='login-submit-btn']")

    def test_login_waits_for_browse_url(self):
        cfg = _make_config()
        auth = NetflixAuth(cfg)
        page = _make_page_mock()

        auth.login(page)

        page.wait_for_url.assert_called_once_with(
            _POST_LOGIN_URL_PATTERN, timeout=cfg.page_timeout_ms
        )

    def test_login_call_order(self):
        """goto → fill email → fill password → click → wait_for_url."""
        cfg = _make_config()
        auth = NetflixAuth(cfg)
        page = _make_page_mock()
        call_log: list[str] = []

        page.goto.side_effect = lambda *a, **kw: call_log.append("goto")
        page.fill.side_effect = lambda *a, **kw: call_log.append(f"fill:{a[0]}")
        page.click.side_effect = lambda *a, **kw: call_log.append("click")
        page.wait_for_url.side_effect = lambda *a, **kw: call_log.append("wait_for_url")

        auth.login(page)

        assert call_log[0] == "goto"
        assert "fill:[data-uia='login-field']" in call_log
        assert "fill:[data-uia='password-field']" in call_log
        assert call_log[-1] == "wait_for_url"
