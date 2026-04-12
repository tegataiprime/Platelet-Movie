"""Unit tests for platelet_movie.tmdb_client."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from platelet_movie.models import Movie

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_tmdb_movie_response(
    movie_id: int,
    title: str,
    runtime: int,
    overview: str = "A movie.",
    genres: list[str] | None = None,
    vote_average: float = 7.5,
    release_date: str = "2024-01-15",
) -> dict:
    """Create a TMDB movie object as returned by the API."""
    genre_list = genres or ["Action", "Drama"]
    return {
        "id": movie_id,
        "title": title,
        "runtime": runtime,
        "overview": overview,
        "release_date": release_date,
        "vote_average": vote_average,
        "genres": [{"id": i, "name": name} for i, name in enumerate(genre_list)],
    }


def _make_discover_response(movies: list[dict], page: int = 1, total_pages: int = 1) -> dict:
    """Create a TMDB discover API response."""
    return {
        "page": page,
        "results": movies,
        "total_pages": total_pages,
        "total_results": len(movies),
    }


def _make_watch_providers_response(
    movie_id: int, has_netflix: bool = True, region: str = "US"
) -> dict:
    """Create a TMDB watch providers API response."""
    providers = {}
    if has_netflix:
        providers[region] = {
            "link": f"https://www.themoviedb.org/movie/{movie_id}/watch?locale={region}",
            "flatrate": [
                {"provider_id": 8, "provider_name": "Netflix"},
            ],
        }
    return {"id": movie_id, "results": providers}


def _make_release_dates_response(
    movie_id: int, certification: str | None = "PG-13", region: str = "US"
) -> dict:
    """Create a TMDB release_dates API response."""
    results = []
    if certification:
        results.append(
            {
                "iso_3166_1": region,
                "release_dates": [
                    {
                        "certification": certification,
                        "release_date": "2024-01-15T00:00:00.000Z",
                        "type": 3,  # Theatrical release
                    }
                ],
            }
        )
    return {"id": movie_id, "results": results}


# ---------------------------------------------------------------------------
# TMDBClient instantiation
# ---------------------------------------------------------------------------


class TestTMDBClientInit:
    def test_requires_api_key(self):
        from platelet_movie.tmdb_client import TMDBClient

        with pytest.raises(ValueError, match="API key"):
            TMDBClient(api_key="")

    def test_accepts_valid_api_key(self):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="valid_key_123")
        assert client._api_key == "valid_key_123"

    def test_default_region_is_us(self):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="key")
        assert client._region == "US"

    def test_custom_region(self):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="key", region="GB")
        assert client._region == "GB"


# ---------------------------------------------------------------------------
# TMDBClient.discover_movies_on_netflix
# ---------------------------------------------------------------------------


class TestDiscoverMoviesOnNetflix:
    def test_returns_list_of_movies(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        # Mock the discover endpoint
        discover_data = _make_discover_response(
            [
                {"id": 1, "title": "Long Movie", "overview": "desc"},
                {"id": 2, "title": "Another Long", "overview": "desc"},
            ]
        )

        # Mock movie details with runtime
        movie_details_1 = _make_tmdb_movie_response(1, "Long Movie", 150)
        movie_details_2 = _make_tmdb_movie_response(2, "Another Long", 140)

        # Mock watch providers (both on Netflix)
        providers_1 = _make_watch_providers_response(1, has_netflix=True)
        providers_2 = _make_watch_providers_response(2, has_netflix=True)

        # Mock release_dates for certification
        release_dates_1 = _make_release_dates_response(1, "PG-13")
        release_dates_2 = _make_release_dates_response(2, "R")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details_1,
            providers_1,
            release_dates_1,
            movie_details_2,
            providers_2,
            release_dates_2,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert isinstance(movies, list)
        assert all(isinstance(m, Movie) for m in movies)

    def test_filters_by_minimum_runtime(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response(
            [
                {"id": 1, "title": "Short Movie", "overview": "desc"},
                {"id": 2, "title": "Long Movie", "overview": "desc"},
            ]
        )

        # Short movie: 90 minutes (filtered by runtime, no providers call)
        # Long movie: 150 minutes (passes runtime, needs providers call)
        movie_details_1 = _make_tmdb_movie_response(1, "Short Movie", 90)
        movie_details_2 = _make_tmdb_movie_response(2, "Long Movie", 150)
        providers_2 = _make_watch_providers_response(2, has_netflix=True)
        release_dates_2 = _make_release_dates_response(2, "PG-13")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        # Order: discover -> movie1_details -> movie2_details -> providers -> release_dates
        # (movie1 is filtered by runtime before providers check)
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details_1,
            movie_details_2,
            providers_2,
            release_dates_2,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert len(movies) == 1
        assert movies[0].title == "Long Movie"
        assert movies[0].runtime_minutes == 150

    def test_excludes_movies_not_on_netflix(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response(
            [
                {"id": 1, "title": "Netflix Movie", "overview": "desc"},
                {"id": 2, "title": "Other Service", "overview": "desc"},
            ]
        )

        movie_details_1 = _make_tmdb_movie_response(1, "Netflix Movie", 150)
        movie_details_2 = _make_tmdb_movie_response(2, "Other Service", 160)
        providers_1 = _make_watch_providers_response(1, has_netflix=True)
        providers_2 = _make_watch_providers_response(2, has_netflix=False)  # Not on Netflix
        release_dates_1 = _make_release_dates_response(1, "PG-13")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details_1,
            providers_1,
            release_dates_1,
            movie_details_2,
            providers_2,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert len(movies) == 1
        assert movies[0].title == "Netflix Movie"

    def test_returns_sorted_by_runtime_then_title(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response(
            [
                {"id": 1, "title": "Zulu", "overview": "desc"},
                {"id": 2, "title": "Alpha", "overview": "desc"},
                {"id": 3, "title": "Beta", "overview": "desc"},
            ]
        )

        # Zulu: 150m, Alpha: 140m, Beta: 140m (same runtime, alphabetically Beta > Alpha)
        movie_details_1 = _make_tmdb_movie_response(1, "Zulu", 150)
        movie_details_2 = _make_tmdb_movie_response(2, "Alpha", 140)
        movie_details_3 = _make_tmdb_movie_response(3, "Beta", 140)
        providers_1 = _make_watch_providers_response(1, has_netflix=True)
        providers_2 = _make_watch_providers_response(2, has_netflix=True)
        providers_3 = _make_watch_providers_response(3, has_netflix=True)
        release_dates_1 = _make_release_dates_response(1, "R")
        release_dates_2 = _make_release_dates_response(2, "PG-13")
        release_dates_3 = _make_release_dates_response(3, "PG")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details_1,
            providers_1,
            release_dates_1,
            movie_details_2,
            providers_2,
            release_dates_2,
            movie_details_3,
            providers_3,
            release_dates_3,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert len(movies) == 3
        # Sorted by runtime ascending, then title ascending
        assert movies[0].title == "Alpha"  # 140m
        assert movies[1].title == "Beta"  # 140m
        assert movies[2].title == "Zulu"  # 150m

    def test_returns_empty_list_when_no_matches(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response([])  # No results

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.return_value = discover_data

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert movies == []

    def test_handles_missing_runtime_field(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response(
            [
                {"id": 1, "title": "No Runtime Movie", "overview": "desc"},
            ]
        )

        # Movie details without runtime field
        movie_details_no_runtime = {
            "id": 1,
            "title": "No Runtime Movie",
            "overview": "A movie.",
            "release_date": "2024-01-15",
            # No "runtime" field
        }
        providers = _make_watch_providers_response(1, has_netflix=True)

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details_no_runtime,
            providers,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        # Movie with missing runtime should be skipped
        assert movies == []

    def test_handles_null_runtime(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response(
            [
                {"id": 1, "title": "Null Runtime", "overview": "desc"},
            ]
        )

        movie_details_null = {
            "id": 1,
            "title": "Null Runtime",
            "runtime": None,  # Explicit null
        }
        providers = _make_watch_providers_response(1, has_netflix=True)

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details_null,
            providers,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert movies == []

    def test_raises_for_negative_min_runtime(self):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        with pytest.raises(ValueError, match="non-negative"):
            client.discover_movies_on_netflix(min_runtime_minutes=-1)

    def test_raises_when_max_runtime_less_than_min(self):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        with pytest.raises(ValueError, match="max_runtime_minutes must be >= min_runtime_minutes"):
            client.discover_movies_on_netflix(min_runtime_minutes=150, max_runtime_minutes=100)

    def test_filters_by_max_runtime(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response(
            [
                {"id": 1, "title": "Short", "overview": "desc"},
                {"id": 2, "title": "Long", "overview": "desc"},
            ]
        )

        short_movie = _make_tmdb_movie_response(1, "Short", 160)
        long_movie = _make_tmdb_movie_response(2, "Long", 200)
        providers_1 = _make_watch_providers_response(1, has_netflix=True)
        providers_2 = _make_watch_providers_response(2, has_netflix=True)
        release_dates_1 = _make_release_dates_response(1, "PG-13")
        release_dates_2 = _make_release_dates_response(2, "R")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            short_movie,
            providers_1,
            release_dates_1,
            long_movie,
            providers_2,
            release_dates_2,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=150, max_runtime_minutes=180)

        titles = [m.title for m in movies]
        assert "Short" in titles
        assert "Long" not in titles

    def test_filters_by_language(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response([])  # No results

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.return_value = discover_data

        client.discover_movies_on_netflix(language="es")

        # Check that the discover call was made with the language param
        mock_get.assert_called()
        call_args = mock_get.call_args
        assert call_args[1]["params"]["with_original_language"] == "es"

    def test_extracts_genres_and_rating(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response(
            [{"id": 1, "title": "Genre Movie", "overview": "desc"}]
        )

        movie_details = _make_tmdb_movie_response(
            1,
            "Genre Movie",
            150,
            genres=["Action", "Sci-Fi", "Thriller"],
            vote_average=8.7,
        )
        providers = _make_watch_providers_response(1, has_netflix=True)
        release_dates = _make_release_dates_response(1, "PG-13")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details,
            providers,
            release_dates,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert len(movies) == 1
        assert movies[0].genres == ["Action", "Sci-Fi", "Thriller"]
        assert movies[0].rating == 8.7
        assert movies[0].certification == "PG-13"

    def test_extracts_year_from_release_date(self, mocker):
        """Test that the year is correctly extracted from release_date."""
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response(
            [{"id": 1, "title": "Inception", "overview": "desc"}]
        )

        movie_details = _make_tmdb_movie_response(
            1,
            "Inception",
            148,
            release_date="2010-07-16",
        )
        providers = _make_watch_providers_response(1, has_netflix=True)
        release_dates = _make_release_dates_response(1, "PG-13")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details,
            providers,
            release_dates,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert len(movies) == 1
        assert movies[0].year == 2010

    def test_handles_missing_release_date(self, mocker):
        """Test that missing release_date results in year being None."""
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response([{"id": 1, "title": "No Year", "overview": "desc"}])

        # Movie details without release_date field
        movie_details = {
            "id": 1,
            "title": "No Year",
            "runtime": 150,
            "vote_average": 7.0,
        }
        providers = _make_watch_providers_response(1, has_netflix=True)
        release_dates = _make_release_dates_response(1, "R")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details,
            providers,
            release_dates,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert len(movies) == 1
        assert movies[0].year is None

    def test_handles_invalid_release_date_format(self, mocker):
        """Test that an invalid release_date format results in year being None."""
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response(
            [{"id": 1, "title": "Bad Date", "overview": "desc"}]
        )

        movie_details = _make_tmdb_movie_response(
            1,
            "Bad Date",
            150,
            release_date="invalid-date",
        )
        providers = _make_watch_providers_response(1, has_netflix=True)
        release_dates = _make_release_dates_response(1, "R")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details,
            providers,
            release_dates,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert len(movies) == 1
        assert movies[0].year is None

    def test_handles_missing_genres(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response(
            [{"id": 1, "title": "No Genre", "overview": "desc"}]
        )

        # Movie details without genres field
        movie_details = {
            "id": 1,
            "title": "No Genre",
            "runtime": 150,
            "vote_average": 7.0,
        }
        providers = _make_watch_providers_response(1, has_netflix=True)
        release_dates = _make_release_dates_response(1, "R")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details,
            providers,
            release_dates,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert len(movies) == 1
        assert movies[0].genres == []
        assert movies[0].rating == 7.0

    def test_handles_missing_rating(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response(
            [{"id": 1, "title": "No Rating", "overview": "desc"}]
        )

        # Movie details without vote_average field
        movie_details = {
            "id": 1,
            "title": "No Rating",
            "runtime": 150,
            "genres": [{"id": 1, "name": "Drama"}],
        }
        providers = _make_watch_providers_response(1, has_netflix=True)
        release_dates = _make_release_dates_response(1, "PG")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details,
            providers,
            release_dates,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert len(movies) == 1
        assert movies[0].genres == ["Drama"]
        assert movies[0].rating is None

    def test_handles_missing_certification(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response([{"id": 1, "title": "No Cert", "overview": "desc"}])

        movie_details = _make_tmdb_movie_response(1, "No Cert", 150)
        providers = _make_watch_providers_response(1, has_netflix=True)
        # No certification available
        release_dates = _make_release_dates_response(1, certification=None)

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details,
            providers,
            release_dates,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert len(movies) == 1
        assert movies[0].certification is None


# ---------------------------------------------------------------------------
# TMDBClient error handling
# ---------------------------------------------------------------------------


class TestTMDBClientErrorHandling:
    def test_raises_on_invalid_api_key(self, mocker):
        from platelet_movie.tmdb_client import TMDBAPIError, TMDBClient

        client = TMDBClient(api_key="invalid_key")

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "status_code": 7,
            "status_message": "Invalid API key.",
        }
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value = mock_response

        with pytest.raises(TMDBAPIError, match="Invalid API key"):
            client.discover_movies_on_netflix()

    def test_raises_on_rate_limit(self, mocker):
        from platelet_movie.tmdb_client import TMDBAPIError, TMDBClient

        client = TMDBClient(api_key="test_key")

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "status_code": 25,
            "status_message": "Your request count is over the allowed limit.",
        }
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value = mock_response

        with pytest.raises(TMDBAPIError, match="rate limit"):
            client.discover_movies_on_netflix()

    def test_raises_on_server_error(self, mocker):
        from platelet_movie.tmdb_client import TMDBAPIError, TMDBClient

        client = TMDBClient(api_key="test_key")

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value = mock_response

        with pytest.raises(TMDBAPIError, match="server error"):
            client.discover_movies_on_netflix()

    def test_raises_on_network_error(self, mocker):
        from platelet_movie.tmdb_client import TMDBAPIError, TMDBClient

        client = TMDBClient(api_key="test_key")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.side_effect = requests.ConnectionError("Network unreachable")

        with pytest.raises(TMDBAPIError, match="(?i)network"):
            client.discover_movies_on_netflix()

    def test_raises_on_timeout(self, mocker):
        from platelet_movie.tmdb_client import TMDBAPIError, TMDBClient

        client = TMDBClient(api_key="test_key")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.side_effect = requests.Timeout("Request timed out")

        with pytest.raises(TMDBAPIError, match="timed out"):
            client.discover_movies_on_netflix()


# ---------------------------------------------------------------------------
# TMDBClient uses correct region
# ---------------------------------------------------------------------------


class TestTMDBClientRegion:
    def test_uses_configured_region_for_providers(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key", region="GB")

        discover_data = _make_discover_response(
            [
                {"id": 1, "title": "UK Movie", "overview": "desc"},
            ]
        )
        movie_details = _make_tmdb_movie_response(1, "UK Movie", 150)
        # Movie is on Netflix in GB, not US
        providers = _make_watch_providers_response(1, has_netflix=True, region="GB")
        release_dates = _make_release_dates_response(1, "15", region="GB")  # UK rating

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details,
            providers,
            release_dates,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert len(movies) == 1
        assert movies[0].title == "UK Movie"
        assert movies[0].certification == "15"

    def test_excludes_movie_not_in_configured_region(self, mocker):
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key", region="GB")

        discover_data = _make_discover_response(
            [
                {"id": 1, "title": "US Only Movie", "overview": "desc"},
            ]
        )
        movie_details = _make_tmdb_movie_response(1, "US Only Movie", 150)
        # Movie is on Netflix in US only, not GB
        providers = _make_watch_providers_response(1, has_netflix=True, region="US")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.side_effect = [
            discover_data,
            movie_details,
            providers,
        ]

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        # Movie should be excluded because it's not on Netflix in GB
        assert movies == []


class TestExceptionHandling:
    """Tests for exception handling in TMDBClient."""

    def test_discover_continues_on_movie_processing_error(self, mocker):
        """Test that discover_movies_on_netflix continues when one movie raises an exception."""
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        # Two movies in discover results
        discover_data = _make_discover_response(
            [
                {"id": 1, "title": "Movie 1", "overview": "desc1"},
                {"id": 2, "title": "Movie 2", "overview": "desc2"},
            ]
        )

        # First movie details will raise an exception
        # Second movie will succeed
        movie2_details = _make_tmdb_movie_response(2, "Movie 2", 140)
        providers2 = _make_watch_providers_response(2, has_netflix=True)
        release_dates2 = _make_release_dates_response(2, certification="PG-13")

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()

        # First call: discover API
        # Second call: movie 1 details - will raise exception
        # Third call: movie 2 details - will succeed
        # Fourth call: movie 2 providers
        # Fifth call: movie 2 release dates
        responses = [
            discover_data,
            Exception("Failed to get movie 1 details"),  # This will be raised
            movie2_details,
            providers2,
            release_dates2,
        ]

        def side_effect_func(*args, **kwargs):
            response = responses.pop(0)
            if isinstance(response, Exception):
                raise response
            return response

        mock_get.return_value.json.side_effect = side_effect_func

        # Should continue processing and return movie 2 despite error on movie 1
        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        assert len(movies) == 1
        assert movies[0].title == "Movie 2"

    def test_certification_api_error_returns_none(self, mocker):
        """Test that _get_certification returns None when API call fails."""
        from platelet_movie.tmdb_client import TMDBClient

        client = TMDBClient(api_key="test_key")

        discover_data = _make_discover_response([{"id": 1, "title": "Movie", "overview": "desc"}])
        movie_details = _make_tmdb_movie_response(1, "Movie", 140)
        providers = _make_watch_providers_response(1, has_netflix=True)

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = MagicMock()

        # Mock responses: discover, movie details, providers, then fail on release_dates
        call_count = [0]

        def side_effect_func(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                mock_get.return_value.json.return_value = discover_data
                return mock_get.return_value
            elif call_count[0] == 2:
                mock_get.return_value.json.return_value = movie_details
                return mock_get.return_value
            elif call_count[0] == 3:
                mock_get.return_value.json.return_value = providers
                return mock_get.return_value
            else:  # release_dates call - raise error
                error = requests.HTTPError()
                error.response = MagicMock()
                error.response.status_code = 404
                error.response.json.return_value = {"status_message": "Not found"}
                raise error

        mock_get.side_effect = side_effect_func

        movies = client.discover_movies_on_netflix(min_runtime_minutes=135)

        # Should succeed with None certification
        assert len(movies) == 1
        assert movies[0].certification is None

    def test_make_request_handles_json_decode_error(self, mocker):
        """Test that _make_request handles JSON decode errors in error responses."""
        from platelet_movie.tmdb_client import TMDBAPIError, TMDBClient

        client = TMDBClient(api_key="test_key")

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.side_effect = ValueError("Invalid JSON")

        error = requests.HTTPError()
        error.response = mock_response

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.raise_for_status.side_effect = error

        with pytest.raises(TMDBAPIError, match="TMDB API error \\(400\\)"):
            client._make_request("http://test.com", {})

    def test_make_request_handles_non_standard_status_codes(self, mocker):
        """Test that _make_request handles status codes other than 401, 429, 500+."""
        from platelet_movie.tmdb_client import TMDBAPIError, TMDBClient

        client = TMDBClient(api_key="test_key")

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"status_message": "Resource not found"}

        error = requests.HTTPError()
        error.response = mock_response

        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.return_value.raise_for_status.side_effect = error

        with pytest.raises(TMDBAPIError, match="TMDB API error \\(404\\): Resource not found"):
            client._make_request("http://test.com", {})

    def test_make_request_handles_generic_request_exception(self, mocker):
        """Test that _make_request handles RequestException."""
        from platelet_movie.tmdb_client import TMDBAPIError, TMDBClient

        client = TMDBClient(api_key="test_key")

        # RequestException that's not HTTPError, ConnectionError, or Timeout
        mock_get = mocker.patch("platelet_movie.tmdb_client.requests.get")
        mock_get.side_effect = requests.RequestException("Generic request error")

        with pytest.raises(TMDBAPIError, match="Request failed: Generic request error"):
            client._make_request("http://test.com", {})
