"""Netflix API client – queries for movies and filters by minimum runtime."""

from __future__ import annotations

import requests

from platelet_movie.auth import NetflixAuth
from platelet_movie.config import Config
from platelet_movie.models import Movie

# uNoGS v1 endpoint for searching Netflix titles
_SEARCH_ENDPOINT = "https://{host}/aaapi.cgi"

# Maximum items to request per API page
_PAGE_SIZE = 100


class NetflixClient:
    """HTTP client that queries the Netflix catalog via the uNoGS RapidAPI.

    Results are filtered to movies whose runtime is at least *min_minutes*
    and sorted ascending by (runtime, title).
    """

    def __init__(self, config: Config, auth: NetflixAuth | None = None) -> None:
        self._config = config
        self._auth = auth or NetflixAuth(config)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_movies(self, min_minutes: int = 135) -> list[Movie]:
        """Return movies with runtime >= *min_minutes*, sorted ascending.

        Paginates through all available results from the API.

        Args:
            min_minutes: Minimum runtime in minutes (inclusive). Defaults to 135.

        Returns:
            Sorted list of :class:`~platelet_movie.models.Movie` instances.
        """
        if min_minutes < 0:
            raise ValueError("min_minutes must be a non-negative integer.")

        movies: list[Movie] = []
        start = 0

        while True:
            batch = self._fetch_page(min_minutes=min_minutes, start=start)
            movies.extend(batch)
            if len(batch) < _PAGE_SIZE:
                break
            start += _PAGE_SIZE

        return sorted(movies)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch_page(self, min_minutes: int, start: int) -> list[Movie]:
        """Fetch a single page of results and parse them into Movie objects."""
        url = _SEARCH_ENDPOINT.format(host=self._config.api_host)
        params = {
            "q": f"get:new!1900,2099-!0,5-!0,10-!{min_minutes},600-!1,1-!Any-!Any",
            "t": "ns",
            "cl": "all",
            "st": "adv",
            "ob": "Relevance",
            "p": str(start // _PAGE_SIZE + 1),
            "sa": "and",
        }

        response = requests.get(
            url,
            headers=self._auth.get_headers(),
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return self._parse_response(response.json(), min_minutes)

    @staticmethod
    def _parse_response(data: dict, min_minutes: int) -> list[Movie]:
        """Parse a raw API response dict into a list of Movie objects.

        Only movies whose runtime meets the *min_minutes* threshold are included.
        """
        movies: list[Movie] = []
        items = data.get("ITEMS", [])
        for item in items:
            title = item.get("title") or item.get("show_title", "")
            # Runtime may be stored as a string like "142 min" or a plain int
            raw_runtime = item.get("runtime") or item.get("runtime_minutes", 0)
            runtime = _parse_runtime(raw_runtime)
            if runtime >= min_minutes:
                movies.append(Movie(title=title, runtime_minutes=runtime))
        return movies


def _parse_runtime(raw: int | str) -> int:
    """Coerce a raw runtime value to an integer number of minutes.

    Handles formats like ``"142"``, ``"142 min"``, and plain integers.
    Returns 0 for values that cannot be parsed.
    """
    if isinstance(raw, int):
        return raw
    try:
        return int(str(raw).split()[0])
    except (ValueError, IndexError):
        return 0
