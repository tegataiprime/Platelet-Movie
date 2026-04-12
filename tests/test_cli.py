"""Unit tests for platelet_movie.cli."""

from click.testing import CliRunner

from platelet_movie.cli import main
from platelet_movie.models import Movie
from platelet_movie.tmdb_client import TMDBAPIError


class TestCLI:
    def _runner(self):
        return CliRunner()

    def _base_env(self, **overrides):
        env = {
            "TMDB_API_KEY": "test_api_key_123",
        }
        env.update(overrides)
        return env

    def test_missing_api_key_exits_with_error(self):
        runner = self._runner()
        result = runner.invoke(main, env={})
        assert result.exit_code == 1
        assert "Configuration error" in result.output
        assert "TMDB_API_KEY" in result.output

    def test_api_error_exits_with_error(self, mocker):
        mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix",
            side_effect=TMDBAPIError("Invalid API key"),
        )
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert result.exit_code == 1
        assert "Error querying TMDB API" in result.output

    def test_no_results_message(self, mocker):
        mocker.patch("platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=[])
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert result.exit_code == 0
        assert "No movies found" in result.output

    def test_results_displayed_sorted(self, mocker):
        movies = [
            Movie(title="Alpha", runtime_minutes=148),
            Movie(title="Zulu", runtime_minutes=200),
        ]
        mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=movies
        )
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert result.exit_code == 0
        assert "Alpha" in result.output
        assert "Zulu" in result.output
        alpha_pos = result.output.index("Alpha")
        zulu_pos = result.output.index("Zulu")
        assert alpha_pos < zulu_pos

    def test_custom_min_minutes_passed_to_client(self, mocker):
        mock_discover = mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=[]
        )
        runner = self._runner()
        runner.invoke(main, ["--min-minutes", "120"], env=self._base_env())
        mock_discover.assert_called_once_with(
            min_runtime_minutes=120, max_runtime_minutes=145, language="en"
        )

    def test_default_min_minutes_is_135(self, mocker):
        mock_discover = mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=[]
        )
        runner = self._runner()
        runner.invoke(main, env=self._base_env())
        mock_discover.assert_called_once_with(
            min_runtime_minutes=135, max_runtime_minutes=145, language="en"
        )

    def test_max_minutes_option(self, mocker):
        mock_discover = mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=[]
        )
        runner = self._runner()
        runner.invoke(main, ["--max-minutes", "180"], env=self._base_env())
        mock_discover.assert_called_once_with(
            min_runtime_minutes=135, max_runtime_minutes=180, language="en"
        )

    def test_min_and_max_minutes_together(self, mocker):
        mock_discover = mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=[]
        )
        runner = self._runner()
        runner.invoke(main, ["--min-minutes", "100", "--max-minutes", "200"], env=self._base_env())
        mock_discover.assert_called_once_with(
            min_runtime_minutes=100, max_runtime_minutes=200, language="en"
        )

    def test_language_option(self, mocker):
        mock_discover = mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=[]
        )
        runner = self._runner()
        runner.invoke(main, ["--language", "es"], env=self._base_env())
        mock_discover.assert_called_once_with(
            min_runtime_minutes=135, max_runtime_minutes=145, language="es"
        )

    def test_default_language_is_english(self, mocker):
        mock_discover = mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=[]
        )
        runner = self._runner()
        runner.invoke(main, env=self._base_env())
        mock_discover.assert_called_once_with(
            min_runtime_minutes=135, max_runtime_minutes=145, language="en"
        )

    def test_region_option(self, mocker):
        """--region should be passed to TMDBClient."""
        captured: dict = {}

        original_init = __import__(
            "platelet_movie.tmdb_client", fromlist=["TMDBClient"]
        ).TMDBClient.__init__

        def capture_init(self_inner, api_key, region="US", max_pages=10):
            captured["region"] = region
            original_init(self_inner, api_key, region, max_pages)

        mocker.patch.object(
            __import__("platelet_movie.tmdb_client", fromlist=["TMDBClient"]).TMDBClient,
            "__init__",
            capture_init,
        )
        mocker.patch("platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=[])

        runner = self._runner()
        runner.invoke(main, ["--region", "GB"], env=self._base_env())
        assert captured.get("region") == "GB"

    def test_default_region_is_us(self, mocker, monkeypatch):
        """When --region is not passed and TMDB_REGION is unset, region=US."""
        monkeypatch.delenv("TMDB_REGION", raising=False)
        captured: dict = {}

        original_init = __import__(
            "platelet_movie.tmdb_client", fromlist=["TMDBClient"]
        ).TMDBClient.__init__

        def capture_init(self_inner, api_key, region="US", max_pages=10):
            captured["region"] = region
            original_init(self_inner, api_key, region, max_pages)

        mocker.patch.object(
            __import__("platelet_movie.tmdb_client", fromlist=["TMDBClient"]).TMDBClient,
            "__init__",
            capture_init,
        )
        mocker.patch("platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=[])

        runner = self._runner()
        runner.invoke(main, env=self._base_env())
        assert captured.get("region") == "US"

    def test_negative_min_minutes_rejected(self):
        runner = self._runner()
        result = runner.invoke(main, ["--min-minutes", "-1"], env=self._base_env())
        assert result.exit_code != 0

    def test_version_option(self):
        runner = self._runner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_output_includes_runtime_column(self, mocker):
        movies = [Movie(title="Epic Film", runtime_minutes=180)]
        mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=movies
        )
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert "180" in result.output
        assert "Epic Film" in result.output

    def test_output_includes_genres_and_rating(self, mocker):
        movies = [
            Movie(
                title="Action Movie",
                runtime_minutes=150,
                genres=["Action", "Sci-Fi"],
                rating=8.5,
            )
        ]
        mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=movies
        )
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert "Action Movie" in result.output
        assert "8.5" in result.output
        assert "Action" in result.output
        assert "Sci-Fi" in result.output

    def test_output_handles_missing_genres_and_rating(self, mocker):
        movies = [Movie(title="Basic Movie", runtime_minutes=140)]
        mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=movies
        )
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert "Basic Movie" in result.output
        assert "N/A" in result.output  # Should show N/A for missing data

    def test_api_key_option_overrides_env(self, mocker):
        mocker.patch("platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=[])
        runner = self._runner()
        result = runner.invoke(
            main,
            ["--api-key", "cli_api_key"],
            env={},  # no env vars set
        )
        assert result.exit_code == 0

    def test_unexpected_error_handled(self, mocker):
        mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix",
            side_effect=RuntimeError("unexpected"),
        )
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert result.exit_code == 1
        assert "Error" in result.output

    def test_no_logging_output_without_verbose(self, mocker):
        """Verify that logging messages don't appear in output when --verbose is not set."""
        movies = [Movie(title="Test Movie", runtime_minutes=140)]
        mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=movies
        )
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert result.exit_code == 0
        # Ensure no logging timestamps or level indicators appear
        assert "INFO" not in result.output
        assert "DEBUG" not in result.output
        assert "WARNING" not in result.output
        # Ensure the actual movie data is present
        assert "Test Movie" in result.output

    def test_logging_output_with_verbose(self, mocker):
        """Verify that logging messages appear when --verbose is set."""
        movies = [Movie(title="Test Movie", runtime_minutes=140)]
        mocker.patch(
            "platelet_movie.cli.TMDBClient.discover_movies_on_netflix", return_value=movies
        )
        runner = self._runner()
        result = runner.invoke(main, ["--verbose"], env=self._base_env())
        assert result.exit_code == 0
        # When verbose, debug logs should appear in stderr (captured by Click's runner)
        # Click's CliRunner captures both stdout and stderr in result.output
        # Verify logging indicators are present
        assert any(
            indicator in result.output
            for indicator in ["DEBUG", "Starting Platelet-Movie CLI", "Arguments:"]
        ), f"Expected logging output with --verbose flag. Got: {result.output[:500]}"
        # The actual movie data should still be present
        assert "Test Movie" in result.output
