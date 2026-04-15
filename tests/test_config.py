"""Unit tests for platelet_movie.config."""

import re
from urllib.parse import urlparse

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

        # Extract URLs from the error message and validate domain properly
        # This prevents CWE-20 issues with substring sanitization
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, msg)
        assert len(urls) > 0, "Error message should contain at least one URL"

        # Verify that at least one URL has the correct themoviedb.org domain
        valid_url_found = False
        for url in urls:
            parsed = urlparse(url)
            # Check exact domain match (themoviedb.org or www.themoviedb.org)
            # or subdomain (*.themoviedb.org)
            if (
                parsed.netloc == "themoviedb.org"
                or parsed.netloc == "www.themoviedb.org"
                or parsed.netloc.endswith(".themoviedb.org")
            ):
                valid_url_found = True
                break

        assert valid_url_found, f"Expected a URL with themoviedb.org domain, found: {urls}"

    def test_url_validation_rejects_malicious_urls(self):
        """Test URL domain validation rejects malicious URLs with domain as substring."""
        # These malicious URLs would pass a naive substring check
        # but should fail proper validation
        malicious_urls = [
            "http://evil.com?redirect=themoviedb.org",
            "http://themoviedb.org.evil.com/settings",
            "http://evil-themoviedb.org.com/api",
            "http://notthemoviedb.org/settings",
            "http://evilthemoviedb.org/api",  # Ends with themoviedb.org but not a subdomain
        ]

        for malicious_url in malicious_urls:
            parsed = urlparse(malicious_url)
            # This is the proper validation logic used in the test above
            is_valid = (
                parsed.netloc == "themoviedb.org"
                or parsed.netloc == "www.themoviedb.org"
                or parsed.netloc.endswith(".themoviedb.org")
            )
            assert not is_valid, f"Malicious URL {malicious_url} should not be valid"

        # Valid URLs should pass
        valid_urls = [
            "https://www.themoviedb.org/settings/api",
            "https://api.themoviedb.org/3/movie",
            "https://themoviedb.org/signup",  # Bare domain without www
        ]

        for valid_url in valid_urls:
            parsed = urlparse(valid_url)
            is_valid = (
                parsed.netloc == "themoviedb.org"
                or parsed.netloc == "www.themoviedb.org"
                or parsed.netloc.endswith(".themoviedb.org")
            )
            assert is_valid, f"Valid URL {valid_url} should be considered valid"
