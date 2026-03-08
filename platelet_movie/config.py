"""Configuration module – reads all settings from environment variables (12-Factor App)."""

import os


class Config:
    """Application configuration sourced entirely from the environment."""

    #: Netflix account e-mail address
    netflix_email: str
    #: Netflix account password
    netflix_password: str
    #: Base URL of the Netflix search API (uNoGS / RapidAPI host)
    api_host: str
    #: API key for the Netflix search API
    api_key: str

    def __init__(
        self,
        netflix_email: str | None = None,
        netflix_password: str | None = None,
        api_host: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.netflix_email = netflix_email or os.environ.get("NETFLIX_EMAIL", "")
        self.netflix_password = netflix_password or os.environ.get("NETFLIX_PASSWORD", "")
        self.api_host = api_host or os.environ.get(
            "NETFLIX_API_HOST", "unogs-unogs-v1.p.rapidapi.com"
        )
        self.api_key = api_key or os.environ.get("NETFLIX_API_KEY", "")

    def validate(self) -> None:
        """Raise *ValueError* if any required configuration value is missing."""
        missing = []
        if not self.netflix_email:
            missing.append("NETFLIX_EMAIL")
        if not self.netflix_password:
            missing.append("NETFLIX_PASSWORD")
        if not self.api_key:
            missing.append("NETFLIX_API_KEY")
        if missing:
            raise ValueError(
                f"Missing required environment variable(s): {', '.join(missing)}"
            )
