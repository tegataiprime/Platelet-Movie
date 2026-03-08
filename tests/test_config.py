"""Unit tests for platelet_movie.config."""

import pytest

from platelet_movie.config import Config


class TestConfig:
    def test_defaults_from_env(self, monkeypatch):
        monkeypatch.setenv("NETFLIX_EMAIL", "user@example.com")
        monkeypatch.setenv("NETFLIX_PASSWORD", "secret")
        monkeypatch.setenv("NETFLIX_API_KEY", "mykey")
        monkeypatch.setenv("NETFLIX_API_HOST", "custom.host.com")

        cfg = Config()
        assert cfg.netflix_email == "user@example.com"
        assert cfg.netflix_password == "secret"
        assert cfg.api_key == "mykey"
        assert cfg.api_host == "custom.host.com"

    def test_constructor_args_override_env(self, monkeypatch):
        monkeypatch.setenv("NETFLIX_EMAIL", "env@example.com")
        cfg = Config(netflix_email="direct@example.com", netflix_password="pw", api_key="k")
        assert cfg.netflix_email == "direct@example.com"

    def test_default_api_host(self, monkeypatch):
        monkeypatch.delenv("NETFLIX_API_HOST", raising=False)
        cfg = Config()
        assert cfg.api_host == "unogs-unogs-v1.p.rapidapi.com"

    def test_empty_config_uses_empty_strings(self, monkeypatch):
        for var in ("NETFLIX_EMAIL", "NETFLIX_PASSWORD", "NETFLIX_API_KEY", "NETFLIX_API_HOST"):
            monkeypatch.delenv(var, raising=False)
        cfg = Config()
        assert cfg.netflix_email == ""
        assert cfg.netflix_password == ""
        assert cfg.api_key == ""

    def test_validate_passes_with_all_fields(self):
        cfg = Config(netflix_email="a@b.com", netflix_password="pw", api_key="k")
        cfg.validate()  # should not raise

    def test_validate_raises_when_email_missing(self):
        cfg = Config(netflix_email="", netflix_password="pw", api_key="k")
        with pytest.raises(ValueError, match="NETFLIX_EMAIL"):
            cfg.validate()

    def test_validate_raises_when_password_missing(self):
        cfg = Config(netflix_email="a@b.com", netflix_password="", api_key="k")
        with pytest.raises(ValueError, match="NETFLIX_PASSWORD"):
            cfg.validate()

    def test_validate_raises_when_api_key_missing(self):
        cfg = Config(netflix_email="a@b.com", netflix_password="pw", api_key="")
        with pytest.raises(ValueError, match="NETFLIX_API_KEY"):
            cfg.validate()

    def test_validate_raises_with_multiple_missing(self):
        cfg = Config()
        with pytest.raises(ValueError) as exc_info:
            cfg.validate()
        msg = str(exc_info.value)
        assert "NETFLIX_EMAIL" in msg
        assert "NETFLIX_PASSWORD" in msg
        assert "NETFLIX_API_KEY" in msg
