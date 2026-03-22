"""Authentication module – handles Netflix login via a Playwright browser page."""

from __future__ import annotations

from typing import TYPE_CHECKING

from platelet_movie.config import Config

if TYPE_CHECKING:
    from playwright.sync_api import Page

# Netflix login page URL
_NETFLIX_LOGIN_URL = "https://www.netflix.com/login"

# Netflix uses stable ``data-uia`` attributes on its login form elements.
_EMAIL_SELECTOR = "[data-uia='login-field']"
_PASSWORD_SELECTOR = "[data-uia='password-field']"
_SUBMIT_SELECTOR = "[data-uia='login-submit-btn']"

# URL glob that indicates a successful login redirect
_POST_LOGIN_URL_PATTERN = "**/browse**"


class NetflixAuth:
    """Handles Netflix account authentication via a Playwright browser page.

    Credentials (e-mail / password) are read from :class:`~platelet_movie.config.Config`
    and entered into the Netflix login form programmatically.
    """

    def __init__(self, config: Config) -> None:
        self._config = config

    def login(self, page: "Page") -> None:
        """Log in to Netflix using the provided Playwright page.

        Navigates to the Netflix login page, fills in the credentials, submits
        the form, and waits until the browser reaches a ``/browse`` URL, which
        indicates successful authentication.

        Args:
            page: A Playwright :class:`~playwright.sync_api.Page` instance.

        Raises:
            playwright.sync_api.TimeoutError: If login does not complete within
                the configured :attr:`~platelet_movie.config.Config.page_timeout_ms`.
        """
        page.goto(_NETFLIX_LOGIN_URL, timeout=self._config.page_timeout_ms)
        page.fill(_EMAIL_SELECTOR, self._config.netflix_email)
        page.fill(_PASSWORD_SELECTOR, self._config.netflix_password)
        page.click(_SUBMIT_SELECTOR)
        page.wait_for_url(_POST_LOGIN_URL_PATTERN, timeout=self._config.page_timeout_ms)
