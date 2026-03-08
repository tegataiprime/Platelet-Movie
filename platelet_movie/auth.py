"""Authentication module – manages Netflix credentials and produces request headers."""

from __future__ import annotations

from platelet_movie.config import Config


class NetflixAuth:
    """Encapsulates authentication details for the Netflix API.

    The credentials (e-mail / password) are kept in memory and used to
    build the HTTP headers required by the uNoGS RapidAPI endpoint.
    Netflix's own credential pair is sent alongside the RapidAPI key so
    that the upstream proxy can validate the subscriber session.
    """

    def __init__(self, config: Config) -> None:
        self._config = config

    def get_headers(self) -> dict[str, str]:
        """Return the HTTP request headers needed to authenticate API calls."""
        return {
            "x-rapidapi-host": self._config.api_host,
            "x-rapidapi-key": self._config.api_key,
            # Netflix account identity forwarded to the API for subscriber lookup
            "x-netflix-email": self._config.netflix_email,
            "x-netflix-password": self._config.netflix_password,
        }
