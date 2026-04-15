"""TMDB API client – discovers Netflix movies using The Movie Database API.

This module replaces the former Playwright-based Netflix scraper with a more
reliable approach using TMDB's public API. TMDB provides watch provider data
that includes Netflix availability by region.

API Documentation: https://developer.themoviedb.org/docs
"""

from __future__ import annotations

import logging

import requests

from platelet_movie.models import Movie

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------
# TMDB API configuration
# -----------------------------------------------------------------------

_TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Netflix provider ID in TMDB's watch providers system
_NETFLIX_PROVIDER_ID = 8

# Default timeout for API requests (seconds)
_DEFAULT_TIMEOUT = 30


class TMDBAPIError(Exception):
    """Raised when the TMDB API returns an error or is unreachable."""


class TMDBClient:
    """Client for The Movie Database (TMDB) API.

    Discovers movies available on Netflix with runtime filtering, using TMDB's
    watch providers data. This approach is more reliable than web scraping
    because TMDB provides a stable, documented API.

    Args:
        api_key: Your TMDB API key (v3 auth). Get one free at
            https://www.themoviedb.org/settings/api
        region: ISO 3166-1 alpha-2 country code for Netflix availability.
            Defaults to "US".
        max_pages: Maximum number of pages to fetch from TMDB discover API.
            Each page contains up to 20 movies. Defaults to 10 (200 movies).

    Raises:
        ValueError: If ``api_key`` is empty.
    """

    def __init__(self, api_key: str, region: str = "US", max_pages: int = 10) -> None:
        if not api_key:
            raise ValueError("TMDB API key is required.")
        self._api_key = api_key
        self._region = region.upper()
        self._max_pages = max(1, max_pages)
        logger.debug(
            f"TMDBClient initialized for region: {self._region}, max_pages: {self._max_pages}"
        )

    def discover_movies_on_netflix(
        self,
        min_runtime_minutes: int = 135,
        max_runtime_minutes: int | None = None,
        language: str = "en",
    ) -> list[Movie]:
        """Discover movies on Netflix with runtime >= min_runtime_minutes.

        Uses TMDB's discover/movie endpoint to find movies, then checks each
        one's watch providers and runtime to filter appropriately.

        Args:
            min_runtime_minutes: Minimum runtime in minutes (inclusive).
                Defaults to 135 (suitable for platelet donation).
            max_runtime_minutes: Maximum runtime in minutes (inclusive).
                If None, no upper limit is applied.
            language: Original language filter (ISO 639-1 code).
                Defaults to "en" (English).

        Returns:
            List of :class:`~platelet_movie.models.Movie` instances, sorted
            ascending by runtime then title.

        Raises:
            ValueError: If ``min_runtime_minutes`` is negative.
            TMDBAPIError: If API returns an error or is unreachable.
        """
        if min_runtime_minutes < 0:
            raise ValueError("min_runtime_minutes must be a non-negative integer.")
        if max_runtime_minutes is not None and max_runtime_minutes < min_runtime_minutes:
            raise ValueError("max_runtime_minutes must be >= min_runtime_minutes.")

        runtime_msg = f">= {min_runtime_minutes}m"
        if max_runtime_minutes:
            runtime_msg = f"{min_runtime_minutes}-{max_runtime_minutes}m"
        logger.info(f"Discovering Netflix movies with runtime {runtime_msg}, language={language}")

        # Get movies that are available on Netflix in the configured region
        # Pre-filter by runtime at the API level for efficiency
        movie_ids = self._discover_movie_ids(
            min_runtime_minutes=min_runtime_minutes,
            max_runtime_minutes=max_runtime_minutes,
            language=language,
        )
        logger.info(f"Found {len(movie_ids)} candidate movies from discover API")

        movies: list[Movie] = []
        for movie_id in movie_ids:
            try:
                movie = self._get_movie_if_on_netflix(
                    movie_id,
                    min_runtime_minutes,
                    max_runtime_minutes,
                )
                if movie:
                    movies.append(movie)
                    logger.debug(f"Found: {movie.title} ({movie.runtime_minutes}m)")
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Error processing movie {movie_id}: {e}")
                continue

        logger.info(f"Found {len(movies)} movies matching criteria")
        return sorted(movies)

    def _discover_movie_ids(
        self,
        min_runtime_minutes: int = 0,
        max_runtime_minutes: int | None = None,
        language: str = "en",
    ) -> list[int]:
        """Discover movie IDs from TMDB that may be on Netflix.

        Fetches multiple pages of results up to max_pages, using TMDB's
        runtime filter to pre-filter results at the API level.
        """
        all_movie_ids: list[int] = []

        for page in range(1, self._max_pages + 1):
            url = f"{_TMDB_BASE_URL}/discover/movie"
            params = {
                "api_key": self._api_key,
                "with_watch_providers": str(_NETFLIX_PROVIDER_ID),
                "watch_region": self._region,
                "sort_by": "popularity.desc",
                "page": page,
                "with_original_language": language,
            }

            # Use TMDB's runtime filter to pre-filter at API level
            if min_runtime_minutes > 0:
                params["with_runtime.gte"] = str(min_runtime_minutes)
            if max_runtime_minutes is not None:
                params["with_runtime.lte"] = str(max_runtime_minutes)

            logger.debug(f"Calling discover API page {page}")
            data = self._make_request(url, params)

            results = data.get("results", [])
            movie_ids = [movie["id"] for movie in results if "id" in movie]
            all_movie_ids.extend(movie_ids)

            total_pages = data.get("total_pages", 1)
            logger.debug(
                f"Page {page}/{min(total_pages, self._max_pages)}: {len(movie_ids)} movies"
            )

            # Stop if we've reached the last page
            if page >= total_pages:
                logger.debug(f"Reached last page ({total_pages})")
                break

        return all_movie_ids

    def _get_movie_if_on_netflix(
        self,
        movie_id: int,
        min_runtime_minutes: int,
        max_runtime_minutes: int | None = None,
    ) -> Movie | None:
        """Get movie details if it meets criteria, or None otherwise."""
        # Get movie details (including runtime)
        details = self._get_movie_details(movie_id)
        runtime = details.get("runtime")
        title = details.get("title", "Unknown")

        if runtime is None or runtime < min_runtime_minutes:
            logger.debug(f"Skipping {title}: runtime={runtime}m")
            return None

        if max_runtime_minutes is not None and runtime > max_runtime_minutes:
            logger.debug(f"Skipping {title}: runtime={runtime}m exceeds max")
            return None

        # Verify Netflix availability in configured region
        if not self._is_on_netflix(movie_id):
            logger.debug(f"Skipping {title}: not on Netflix in {self._region}")
            return None

        # Extract genres (TMDB returns list of {id, name} objects)
        genre_objects = details.get("genres", [])
        genres = [g.get("name") for g in genre_objects if g.get("name")]

        # Extract rating (vote_average is 0-10 scale)
        rating = details.get("vote_average")
        if rating is not None:
            rating = round(rating, 1)

        # Get MPAA certification (R, PG-13, etc.)
        certification = self._get_certification(movie_id)

        # Extract year from release_date (format: "YYYY-MM-DD")
        year = None
        release_date = details.get("release_date")
        if release_date:
            try:
                year = int(release_date.split("-")[0])
            except (ValueError, IndexError):
                # Invalid date format - year remains None
                pass

        return Movie(
            title=title,
            runtime_minutes=runtime,
            genres=genres,
            rating=rating,
            certification=certification,
            year=year,
        )

    def _get_movie_details(self, movie_id: int) -> dict:
        """Get detailed information about a movie."""
        url = f"{_TMDB_BASE_URL}/movie/{movie_id}"
        params = {"api_key": self._api_key}
        return self._make_request(url, params)

    def _get_certification(self, movie_id: int) -> str | None:
        """Get the MPAA certification (R, PG-13, etc.) for a movie.

        Fetches from TMDB's release_dates endpoint and returns the
        certification for the configured region.
        """
        url = f"{_TMDB_BASE_URL}/movie/{movie_id}/release_dates"
        params = {"api_key": self._api_key}

        try:
            data = self._make_request(url, params)
        except TMDBAPIError:
            # Non-critical - continue without certification
            return None

        results = data.get("results", [])

        # Find certification for the configured region
        for country in results:
            if country.get("iso_3166_1") == self._region:
                release_dates = country.get("release_dates", [])
                for release in release_dates:
                    cert = release.get("certification")
                    if cert:  # Return first non-empty certification
                        return cert

        return None

    def _is_on_netflix(self, movie_id: int) -> bool:
        """Check if a movie is available on Netflix in the configured region."""
        url = f"{_TMDB_BASE_URL}/movie/{movie_id}/watch/providers"
        params = {"api_key": self._api_key}

        data = self._make_request(url, params)
        results = data.get("results", {})

        # Check if Netflix is a flatrate provider in the configured region
        region_data = results.get(self._region, {})
        flatrate_providers = region_data.get("flatrate", [])

        for provider in flatrate_providers:
            if provider.get("provider_id") == _NETFLIX_PROVIDER_ID:
                return True

        return False

    def _make_request(self, url: str, params: dict) -> dict:
        """Make an HTTP GET request to TMDB API with error handling."""
        try:
            response = requests.get(url, params=params, timeout=_DEFAULT_TIMEOUT)
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            status_code = e.response.status_code if e.response else 0
            try:
                error_data = e.response.json() if e.response else {}
                message = error_data.get("status_message", str(e))
            except Exception:
                message = str(e)

            if status_code == 401:
                raise TMDBAPIError(f"Invalid API key: {message}") from e
            elif status_code == 429:
                raise TMDBAPIError(
                    f"TMDB rate limit exceeded. Please wait and try again: {message}"
                ) from e
            elif status_code >= 500:
                raise TMDBAPIError(f"TMDB server error ({status_code}): {message}") from e
            else:
                raise TMDBAPIError(f"TMDB API error ({status_code}): {message}") from e

        except requests.ConnectionError as e:
            raise TMDBAPIError(f"Network error: Unable to connect to TMDB API: {e}") from e

        except requests.Timeout as e:
            raise TMDBAPIError(f"Request timed out while connecting to TMDB: {e}") from e

        except requests.RequestException as e:
            raise TMDBAPIError(f"Request failed: {e}") from e
