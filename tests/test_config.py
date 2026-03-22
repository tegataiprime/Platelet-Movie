"""Unit tests for platelet_movie.config."""

import pytest

from platelet_movie.config import Config, _env_bool


class TestConfig:
    def test_defaults_from_env(self, monkeypatch):
        monkeypatch.setenv("NETFLIX_EMAIL", "user@example.com")
        monkeypatch.setenv("NETFLIX_PASSWORD", "secret")

        cfg = Config()
        assert cfg.netflix_email == "user@example.com"
        assert cfg.netflix_password == "secret"

    def test_constructor_args_override_env(self, monkeypatch):
        monkeypatch.setenv("NETFLIX_EMAIL", "env@example.com")
        cfg = Config(netflix_email="direct@example.com", netflix_password="pw")
        assert cfg.netflix_email == "direct@example.com"

    def test_empty_config_uses_empty_strings(self, monkeypatch):
        for var in ("NETFLIX_EMAIL", "NETFLIX_PASSWORD"):
            monkeypatch.delenv(var, raising=False)
        cfg = Config()
        assert cfg.netflix_email == ""
        assert cfg.netflix_password == ""

    # ------------------------------------------------------------------
    # headless
    # ------------------------------------------------------------------

    def test_default_headless_is_true(self, monkeypatch):
        monkeypatch.delenv("NETFLIX_HEADLESS", raising=False)
        cfg = Config()
        assert cfg.headless is True

    def test_headless_from_env_true(self, monkeypatch):
        monkeypatch.setenv("NETFLIX_HEADLESS", "true")
        cfg = Config()
        assert cfg.headless is True

    def test_headless_from_env_false(self, monkeypatch):
        monkeypatch.setenv("NETFLIX_HEADLESS", "false")
        cfg = Config()
        assert cfg.headless is False

    def test_headless_constructor_overrides_env(self, monkeypatch):
        monkeypatch.setenv("NETFLIX_HEADLESS", "false")
        cfg = Config(headless=True)
        assert cfg.headless is True

    # ------------------------------------------------------------------
    # request_delay_s
    # ------------------------------------------------------------------

    def test_default_request_delay(self, monkeypatch):
        monkeypatch.delenv("NETFLIX_REQUEST_DELAY_S", raising=False)
        cfg = Config()
        assert cfg.request_delay_s == 2.0

    def test_request_delay_from_env(self, monkeypatch):
        monkeypatch.setenv("NETFLIX_REQUEST_DELAY_S", "3.5")
        cfg = Config()
        assert cfg.request_delay_s == 3.5

    def test_request_delay_constructor_override(self):
        cfg = Config(request_delay_s=1.0)
        assert cfg.request_delay_s == 1.0

    # ------------------------------------------------------------------
    # page_timeout_ms
    # ------------------------------------------------------------------

    def test_default_page_timeout(self, monkeypatch):
        monkeypatch.delenv("NETFLIX_PAGE_TIMEOUT_MS", raising=False)
        cfg = Config()
        assert cfg.page_timeout_ms == 30000

    def test_page_timeout_from_env(self, monkeypatch):
        monkeypatch.setenv("NETFLIX_PAGE_TIMEOUT_MS", "15000")
        cfg = Config()
        assert cfg.page_timeout_ms == 15000

    def test_page_timeout_constructor_override(self):
        cfg = Config(page_timeout_ms=5000)
        assert cfg.page_timeout_ms == 5000

    # ------------------------------------------------------------------
    # max_movies
    # ------------------------------------------------------------------

    def test_default_max_movies(self, monkeypatch):
        monkeypatch.delenv("NETFLIX_MAX_MOVIES", raising=False)
        cfg = Config()
        assert cfg.max_movies == 100

    def test_max_movies_from_env(self, monkeypatch):
        monkeypatch.setenv("NETFLIX_MAX_MOVIES", "50")
        cfg = Config()
        assert cfg.max_movies == 50

    def test_max_movies_constructor_override(self):
        cfg = Config(max_movies=10)
        assert cfg.max_movies == 10

    # ------------------------------------------------------------------
    # validate()
    # ------------------------------------------------------------------

    def test_validate_passes_with_all_fields(self):
        cfg = Config(netflix_email="a@b.com", netflix_password="pw")
        cfg.validate()  # should not raise

    def test_validate_raises_when_email_missing(self):
        cfg = Config(netflix_email="", netflix_password="pw")
        with pytest.raises(ValueError, match="NETFLIX_EMAIL"):
            cfg.validate()

    def test_validate_raises_when_password_missing(self):
        cfg = Config(netflix_email="a@b.com", netflix_password="")
        with pytest.raises(ValueError, match="NETFLIX_PASSWORD"):
            cfg.validate()

    def test_validate_raises_with_multiple_missing(self, monkeypatch):
        for var in ("NETFLIX_EMAIL", "NETFLIX_PASSWORD"):
            monkeypatch.delenv(var, raising=False)
        cfg = Config()
        with pytest.raises(ValueError) as exc_info:
            cfg.validate()
        msg = str(exc_info.value)
        assert "NETFLIX_EMAIL" in msg
        assert "NETFLIX_PASSWORD" in msg


class TestEnvBool:
    def test_returns_default_when_not_set(self, monkeypatch):
        monkeypatch.delenv("MY_FLAG", raising=False)
        assert _env_bool("MY_FLAG", default=True) is True
        assert _env_bool("MY_FLAG", default=False) is False

    def test_truthy_values(self, monkeypatch):
        for val in ("1", "true", "True", "TRUE", "yes", "Yes", "on", "ON"):
            monkeypatch.setenv("MY_FLAG", val)
            assert _env_bool("MY_FLAG", default=False) is True

    def test_falsy_values(self, monkeypatch):
        for val in ("0", "false", "False", "no", "off", ""):
            monkeypatch.setenv("MY_FLAG", val)
            assert _env_bool("MY_FLAG", default=True) is False
