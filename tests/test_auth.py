"""Unit tests for platelet_movie.auth."""

from platelet_movie.auth import NetflixAuth
from platelet_movie.config import Config


class TestNetflixAuth:
    def _make_config(self, **kwargs):
        defaults = {
            "netflix_email": "user@example.com",
            "netflix_password": "secret",
            "api_key": "testkey",
            "api_host": "api.example.com",
        }
        defaults.update(kwargs)
        return Config(**defaults)

    def test_get_headers_contains_rapidapi_host(self):
        auth = NetflixAuth(self._make_config())
        headers = auth.get_headers()
        assert headers["x-rapidapi-host"] == "api.example.com"

    def test_get_headers_contains_rapidapi_key(self):
        auth = NetflixAuth(self._make_config())
        headers = auth.get_headers()
        assert headers["x-rapidapi-key"] == "testkey"

    def test_get_headers_contains_netflix_email(self):
        auth = NetflixAuth(self._make_config(netflix_email="me@example.com"))
        headers = auth.get_headers()
        assert headers["x-netflix-email"] == "me@example.com"

    def test_get_headers_contains_netflix_password(self):
        auth = NetflixAuth(self._make_config(netflix_password="mypassword"))
        headers = auth.get_headers()
        assert headers["x-netflix-password"] == "mypassword"

    def test_default_auth_created_from_config(self):
        cfg = self._make_config()
        auth = NetflixAuth(cfg)
        assert auth._config is cfg

    def test_headers_are_new_dict_each_call(self):
        auth = NetflixAuth(self._make_config())
        h1 = auth.get_headers()
        h2 = auth.get_headers()
        assert h1 == h2
        assert h1 is not h2
