"""Unit tests for platelet_movie.cli."""

from click.testing import CliRunner

from platelet_movie.cli import main
from platelet_movie.models import Movie


class TestCLI:
    def _runner(self):
        return CliRunner()

    def _base_env(self, **overrides):
        env = {
            "NETFLIX_EMAIL": "user@example.com",
            "NETFLIX_PASSWORD": "secret",
        }
        env.update(overrides)
        return env

    def test_missing_credentials_exits_with_error(self):
        runner = self._runner()
        result = runner.invoke(main, env={})
        assert result.exit_code == 1
        assert "Configuration error" in result.output

    def test_api_error_exits_with_error(self, mocker):
        mocker.patch(
            "platelet_movie.cli.NetflixScraper.get_movies",
            side_effect=RuntimeError("connection refused"),
        )
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert result.exit_code == 1
        assert "Error scraping Netflix" in result.output

    def test_no_results_message(self, mocker):
        mocker.patch("platelet_movie.cli.NetflixScraper.get_movies", return_value=[])
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert result.exit_code == 0
        assert "No movies found" in result.output

    def test_results_displayed_sorted(self, mocker):
        movies = [
            Movie(title="Alpha", runtime_minutes=148),
            Movie(title="Zulu", runtime_minutes=200),
        ]
        mocker.patch("platelet_movie.cli.NetflixScraper.get_movies", return_value=movies)
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert result.exit_code == 0
        assert "Alpha" in result.output
        assert "Zulu" in result.output
        alpha_pos = result.output.index("Alpha")
        zulu_pos = result.output.index("Zulu")
        assert alpha_pos < zulu_pos

    def test_custom_min_minutes_passed_to_scraper(self, mocker):
        mock_get = mocker.patch(
            "platelet_movie.cli.NetflixScraper.get_movies", return_value=[]
        )
        runner = self._runner()
        runner.invoke(main, ["--min-minutes", "120"], env=self._base_env())
        mock_get.assert_called_once_with(min_minutes=120)

    def test_default_min_minutes_is_135(self, mocker):
        mock_get = mocker.patch(
            "platelet_movie.cli.NetflixScraper.get_movies", return_value=[]
        )
        runner = self._runner()
        runner.invoke(main, env=self._base_env())
        mock_get.assert_called_once_with(min_minutes=135)

    def test_no_headless_flag_sets_headless_false(self, mocker):
        """--no-headless should cause Config.headless to be False."""
        captured: dict = {}

        def capture_init(self_inner, config, auth=None):
            captured["headless"] = config.headless

        mocker.patch.object(
            __import__("platelet_movie.scraper", fromlist=["NetflixScraper"]).NetflixScraper,
            "__init__",
            capture_init,
        )
        mocker.patch("platelet_movie.cli.NetflixScraper.get_movies", return_value=[])

        runner = self._runner()
        runner.invoke(main, ["--no-headless"], env=self._base_env())
        assert captured.get("headless") is False

    def test_headless_defaults_to_true_without_flag(self, mocker, monkeypatch):
        """When --no-headless is not passed and NETFLIX_HEADLESS is unset, headless=True."""
        monkeypatch.delenv("NETFLIX_HEADLESS", raising=False)
        captured: dict = {}

        def capture_init(self_inner, config, auth=None):
            captured["headless"] = config.headless

        mocker.patch.object(
            __import__("platelet_movie.scraper", fromlist=["NetflixScraper"]).NetflixScraper,
            "__init__",
            capture_init,
        )
        mocker.patch("platelet_movie.cli.NetflixScraper.get_movies", return_value=[])

        runner = self._runner()
        runner.invoke(main, env=self._base_env())
        assert captured.get("headless") is True

    def test_request_delay_option(self, mocker):
        captured: dict = {}

        def capture_init(self_inner, config, auth=None):
            captured["delay"] = config.request_delay_s

        mocker.patch.object(
            __import__("platelet_movie.scraper", fromlist=["NetflixScraper"]).NetflixScraper,
            "__init__",
            capture_init,
        )
        mocker.patch("platelet_movie.cli.NetflixScraper.get_movies", return_value=[])

        runner = self._runner()
        runner.invoke(main, ["--request-delay", "3.5"], env=self._base_env())
        assert captured.get("delay") == 3.5

    def test_max_movies_option(self, mocker):
        captured: dict = {}

        def capture_init(self_inner, config, auth=None):
            captured["max_movies"] = config.max_movies

        mocker.patch.object(
            __import__("platelet_movie.scraper", fromlist=["NetflixScraper"]).NetflixScraper,
            "__init__",
            capture_init,
        )
        mocker.patch("platelet_movie.cli.NetflixScraper.get_movies", return_value=[])

        runner = self._runner()
        runner.invoke(main, ["--max-movies", "25"], env=self._base_env())
        assert captured.get("max_movies") == 25

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
        mocker.patch("platelet_movie.cli.NetflixScraper.get_movies", return_value=movies)
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert "180" in result.output
        assert "Epic Film" in result.output

    def test_email_option_overrides_env(self, mocker):
        mocker.patch("platelet_movie.cli.NetflixScraper.get_movies", return_value=[])
        runner = self._runner()
        result = runner.invoke(
            main,
            ["--email", "cli@example.com", "--password", "clipass"],
            env={},  # no env vars set
        )
        assert result.exit_code == 0
