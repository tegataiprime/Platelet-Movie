"""Unit tests for platelet_movie.config."""

import pytest

from platelet_movie.config import Config


class TestConfig:
    def test_defaults_from_env(self, monkeypatch):
        monkeypatch.setenv("TMDB_API_KEY", "abc123")

        cfg = Config()
        assert cfg.tmdb_api_key == "abc123"

    def test_constructor_args_override_env(self, monkeypatch):
        monkeypatch.setenv("TMDB_API_KEY", "env_key")
        cfg = Config(tmdb_api_key="direct_key")
        assert cfg.tmdb_api_key == "direct_key"

    def test_empty_config_uses_empty_string(self, monkeypatch):
        monkeypatch.delenv("TMDB_API_KEY", raising=False)
        cfg = Config()
        assert cfg.tmdb_api_key == ""

    # ------------------------------------------------------------------
    # tmdb_region
    # ------------------------------------------------------------------

    def test_default_region_is_us(self, monkeypatch):
        monkeypatch.delenv("TMDB_REGION", raising=False)
        cfg = Config()
        assert cfg.tmdb_region == "US"

    def test_region_from_env(self, monkeypatch):
        monkeypatch.setenv("TMDB_REGION", "GB")
        cfg = Config()
        assert cfg.tmdb_region == "GB"

    def test_region_constructor_override(self, monkeypatch):
        monkeypatch.setenv("TMDB_REGION", "GB")
        cfg = Config(tmdb_region="CA")
        assert cfg.tmdb_region == "CA"

    # ------------------------------------------------------------------
    # validate()
    # ------------------------------------------------------------------

    def test_validate_passes_with_api_key(self):
        cfg = Config(tmdb_api_key="valid_key")
        cfg.validate()  # should not raise

    def test_validate_raises_when_api_key_missing(self, monkeypatch):
        # Ensure environment variable is also not set
        monkeypatch.delenv("TMDB_API_KEY", raising=False)
        cfg = Config(tmdb_api_key="")
        with pytest.raises(ValueError, match="TMDB_API_KEY"):
            cfg.validate()

    def test_validate_raises_with_helpful_message(self, monkeypatch):
        monkeypatch.delenv("TMDB_API_KEY", raising=False)
        cfg = Config()
        with pytest.raises(ValueError) as exc_info:
            cfg.validate()
        msg = str(exc_info.value)
        assert "TMDB_API_KEY" in msg
        assert "themoviedb.org" in msg  # Should include signup URL
