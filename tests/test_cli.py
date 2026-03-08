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
            "NETFLIX_API_KEY": "testkey",
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
            "platelet_movie.cli.NetflixClient.get_movies",
            side_effect=RuntimeError("connection refused"),
        )
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert result.exit_code == 1
        assert "Error querying Netflix API" in result.output

    def test_no_results_message(self, mocker):
        mocker.patch("platelet_movie.cli.NetflixClient.get_movies", return_value=[])
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert result.exit_code == 0
        assert "No movies found" in result.output

    def test_results_displayed_sorted(self, mocker):
        movies = [
            Movie(title="Alpha", runtime_minutes=148),
            Movie(title="Zulu", runtime_minutes=200),
        ]
        mocker.patch("platelet_movie.cli.NetflixClient.get_movies", return_value=movies)
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert result.exit_code == 0
        assert "Alpha" in result.output
        assert "Zulu" in result.output
        alpha_pos = result.output.index("Alpha")
        zulu_pos = result.output.index("Zulu")
        assert alpha_pos < zulu_pos

    def test_custom_min_minutes_passed_to_client(self, mocker):
        mock_get = mocker.patch(
            "platelet_movie.cli.NetflixClient.get_movies", return_value=[]
        )
        runner = self._runner()
        runner.invoke(main, ["--min-minutes", "120"], env=self._base_env())
        mock_get.assert_called_once_with(min_minutes=120)

    def test_default_min_minutes_is_135(self, mocker):
        mock_get = mocker.patch(
            "platelet_movie.cli.NetflixClient.get_movies", return_value=[]
        )
        runner = self._runner()
        runner.invoke(main, env=self._base_env())
        mock_get.assert_called_once_with(min_minutes=135)

    def test_cli_options_override_env_vars(self, mocker):
        def fake_get_movies(min_minutes=135):
            return []

        mocker.patch("platelet_movie.cli.NetflixClient.get_movies", side_effect=fake_get_movies)
        mocker.patch("platelet_movie.cli.Config.validate")

        runner = self._runner()
        result = runner.invoke(
            main,
            ["--email", "cli@example.com", "--password", "clipass", "--api-key", "clikey"],
            env=self._base_env(),
        )
        assert result.exit_code == 0

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
        mocker.patch("platelet_movie.cli.NetflixClient.get_movies", return_value=movies)
        runner = self._runner()
        result = runner.invoke(main, env=self._base_env())
        assert "180" in result.output
        assert "Epic Film" in result.output
