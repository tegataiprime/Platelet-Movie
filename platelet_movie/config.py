"""Configuration module – reads all settings from environment variables (12-Factor App)."""

import os


class Config:
    """Application configuration sourced entirely from the environment."""

    #: Netflix account e-mail address
    netflix_email: str
    #: Netflix account password
    netflix_password: str
    #: Whether to run the Playwright browser in headless mode
    headless: bool
    #: Minimum seconds to wait between page loads (rate-limiting safeguard)
    request_delay_s: float
    #: Playwright page-load timeout in milliseconds
    page_timeout_ms: int
    #: Maximum number of movie detail pages to visit per session
    max_movies: int

    def __init__(
        self,
        netflix_email: str | None = None,
        netflix_password: str | None = None,
        headless: bool | None = None,
        request_delay_s: float | None = None,
        page_timeout_ms: int | None = None,
        max_movies: int | None = None,
    ) -> None:
        self.netflix_email = netflix_email or os.environ.get("NETFLIX_EMAIL", "")
        self.netflix_password = netflix_password or os.environ.get("NETFLIX_PASSWORD", "")
        self.headless = (
            headless if headless is not None else _env_bool("NETFLIX_HEADLESS", default=True)
        )
        self.request_delay_s = (
            request_delay_s
            if request_delay_s is not None
            else float(os.environ.get("NETFLIX_REQUEST_DELAY_S", "2.0"))
        )
        self.page_timeout_ms = (
            page_timeout_ms
            if page_timeout_ms is not None
            else int(os.environ.get("NETFLIX_PAGE_TIMEOUT_MS", "30000"))
        )
        self.max_movies = (
            max_movies
            if max_movies is not None
            else int(os.environ.get("NETFLIX_MAX_MOVIES", "100"))
        )

    def validate(self) -> None:
        """Raise *ValueError* if any required configuration value is missing."""
        missing = []
        if not self.netflix_email:
            missing.append("NETFLIX_EMAIL")
        if not self.netflix_password:
            missing.append("NETFLIX_PASSWORD")
        if missing:
            raise ValueError(
                f"Missing required environment variable(s): {', '.join(missing)}"
            )


def _env_bool(name: str, default: bool) -> bool:
    """Read a boolean environment variable.

    Truthy values: ``1``, ``true``, ``yes``, ``on`` (case-insensitive).
    Returns *default* when the variable is not set.
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}
