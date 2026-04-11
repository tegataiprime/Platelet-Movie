"""Configuration module – reads all settings from environment variables (12-Factor App)."""

import logging
import os

logger = logging.getLogger(__name__)


class Config:
    """Application configuration sourced entirely from the environment.

    This configuration is used for the TMDB API client which provides Netflix
    movie availability data.
    """

    #: TMDB API key (v3 auth)
    tmdb_api_key: str
    #: Region for Netflix availability (ISO 3166-1 alpha-2, e.g., "US", "GB")
    tmdb_region: str
    #: Maximum number of pages to fetch from TMDB API (20 results per page)
    max_pages: int

    def __init__(
        self,
        tmdb_api_key: str | None = None,
        tmdb_region: str | None = None,
        max_pages: int | None = None,
    ) -> None:
        logger.debug("Initializing configuration")
        self.tmdb_api_key = tmdb_api_key or os.environ.get("TMDB_API_KEY", "")
        logger.debug(f"TMDB API key configured: {bool(self.tmdb_api_key)}")

        self.tmdb_region = (
            tmdb_region if tmdb_region is not None else os.environ.get("TMDB_REGION", "US")
        )
        logger.debug(f"TMDB region: {self.tmdb_region}")

        self.max_pages = (
            max_pages
            if max_pages is not None
            else int(os.environ.get("TMDB_MAX_PAGES", "10"))
        )
        logger.debug(f"Max pages: {self.max_pages}")

    def validate(self) -> None:
        """Raise *ValueError* if any required configuration value is missing."""
        logger.debug("Validating configuration")
        if not self.tmdb_api_key:
            logger.error("Missing required configuration: TMDB_API_KEY")
            raise ValueError(
                "Missing required environment variable: TMDB_API_KEY. "
                "Get a free API key at https://www.themoviedb.org/settings/api"
            )
        logger.debug("Configuration validation passed")
