"""Unit tests for platelet_movie.client."""

import pytest
import responses as rsps_lib

from platelet_movie.client import NetflixClient, _parse_runtime
from platelet_movie.config import Config


def _make_config():
    return Config(
        netflix_email="user@example.com",
        netflix_password="secret",
        api_key="testkey",
        api_host="unogs-unogs-v1.p.rapidapi.com",
    )


API_URL = "https://unogs-unogs-v1.p.rapidapi.com/aaapi.cgi"


class TestParseRuntime:
    def test_integer_passthrough(self):
        assert _parse_runtime(142) == 142

    def test_string_integer(self):
        assert _parse_runtime("142") == 142

    def test_string_with_unit(self):
        assert _parse_runtime("142 min") == 142

    def test_zero_for_invalid_string(self):
        assert _parse_runtime("n/a") == 0

    def test_zero_for_empty_string(self):
        assert _parse_runtime("") == 0

    def test_zero_integer(self):
        assert _parse_runtime(0) == 0


class TestNetflixClientGetMovies:
    def _api_response(self, items: list[dict]) -> dict:
        return {"ITEMS": items}

    @rsps_lib.activate
    def test_returns_movies_above_threshold(self):
        items = [
            {"title": "Long Movie", "runtime": 180},
            {"title": "Short Movie", "runtime": 90},
        ]
        rsps_lib.add(rsps_lib.GET, API_URL, json=self._api_response(items), status=200)
        client = NetflixClient(_make_config())
        movies = client.get_movies(min_minutes=135)
        assert len(movies) == 1
        assert movies[0].title == "Long Movie"

    @rsps_lib.activate
    def test_returns_movies_equal_to_threshold(self):
        items = [{"title": "Exact", "runtime": 135}]
        rsps_lib.add(rsps_lib.GET, API_URL, json=self._api_response(items), status=200)
        client = NetflixClient(_make_config())
        movies = client.get_movies(min_minutes=135)
        assert len(movies) == 1
        assert movies[0].runtime_minutes == 135

    @rsps_lib.activate
    def test_results_sorted_ascending(self):
        items = [
            {"title": "Zulu", "runtime": 200},
            {"title": "Alpha", "runtime": 148},
            {"title": "Beta", "runtime": 148},
        ]
        rsps_lib.add(rsps_lib.GET, API_URL, json=self._api_response(items), status=200)
        client = NetflixClient(_make_config())
        movies = client.get_movies(min_minutes=135)
        assert movies[0].title == "Alpha"
        assert movies[1].title == "Beta"
        assert movies[2].title == "Zulu"

    @rsps_lib.activate
    def test_empty_response(self):
        rsps_lib.add(rsps_lib.GET, API_URL, json=self._api_response([]), status=200)
        client = NetflixClient(_make_config())
        movies = client.get_movies(min_minutes=135)
        assert movies == []

    @rsps_lib.activate
    def test_parses_show_title_fallback(self):
        items = [{"show_title": "Fallback Title", "runtime": 150}]
        rsps_lib.add(rsps_lib.GET, API_URL, json=self._api_response(items), status=200)
        client = NetflixClient(_make_config())
        movies = client.get_movies(min_minutes=135)
        assert movies[0].title == "Fallback Title"

    @rsps_lib.activate
    def test_parses_runtime_minutes_fallback(self):
        items = [{"title": "Some Movie", "runtime_minutes": 160}]
        rsps_lib.add(rsps_lib.GET, API_URL, json=self._api_response(items), status=200)
        client = NetflixClient(_make_config())
        movies = client.get_movies(min_minutes=135)
        assert movies[0].runtime_minutes == 160

    @rsps_lib.activate
    def test_http_error_raises(self):
        rsps_lib.add(rsps_lib.GET, API_URL, status=401)
        client = NetflixClient(_make_config())
        with pytest.raises(Exception):
            client.get_movies()

    def test_negative_min_minutes_raises(self):
        client = NetflixClient(_make_config())
        with pytest.raises(ValueError, match="non-negative"):
            client.get_movies(min_minutes=-1)

    @rsps_lib.activate
    def test_pagination_stops_when_partial_page(self):
        """If the first page has fewer than PAGE_SIZE items, no second call is made."""
        items = [{"title": f"Movie {i}", "runtime": 140} for i in range(5)]
        rsps_lib.add(rsps_lib.GET, API_URL, json=self._api_response(items), status=200)
        client = NetflixClient(_make_config())
        movies = client.get_movies(min_minutes=135)
        assert len(movies) == 5

    @rsps_lib.activate
    def test_pagination_fetches_multiple_pages(self):
        """If the first page is full (100 items), a second page is fetched."""
        page1_items = [{"title": f"Movie {i}", "runtime": 140} for i in range(100)]
        page2_items = [{"title": "Last Movie", "runtime": 140}]
        rsps_lib.add(rsps_lib.GET, API_URL, json=self._api_response(page1_items), status=200)
        rsps_lib.add(rsps_lib.GET, API_URL, json=self._api_response(page2_items), status=200)
        client = NetflixClient(_make_config())
        movies = client.get_movies(min_minutes=135)
        assert len(movies) == 101

    @rsps_lib.activate
    def test_string_runtime_is_parsed(self):
        items = [{"title": "Parsed", "runtime": "142 min"}]
        rsps_lib.add(rsps_lib.GET, API_URL, json=self._api_response(items), status=200)
        client = NetflixClient(_make_config())
        movies = client.get_movies(min_minutes=135)
        assert movies[0].runtime_minutes == 142
