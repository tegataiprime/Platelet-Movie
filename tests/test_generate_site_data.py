"""Tests for scripts/generate_site_data.py."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

# Import after modifying path to include scripts directory
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
from generate_site_data import (  # noqa: E402
    generate_site_data,
    get_commentary,
    get_movie_data,
    run_command,
)


class TestRunCommand:
    """Tests for run_command function."""

    @patch("subprocess.run")
    def test_successful_command_returns_stdout(self, mock_run):
        """Test that successful command execution returns stdout."""
        mock_result = MagicMock()
        mock_result.stdout = "command output"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = run_command(["echo", "hello"])

        assert result == "command output"
        mock_run.assert_called_once_with(
            ["echo", "hello"],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("subprocess.run")
    @patch("sys.stderr", new_callable=StringIO)
    def test_failed_command_prints_error_and_raises(self, mock_stderr, mock_run):
        """Test that failed command prints error to stderr and raises exception."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["fake-command"],
            stderr="command failed",
        )

        with pytest.raises(subprocess.CalledProcessError):
            run_command(["fake-command"])

        assert "Error running command" in mock_stderr.getvalue()
        assert "command failed" in mock_stderr.getvalue()


class TestGetMovieData:
    """Tests for get_movie_data function."""

    @patch("generate_site_data.run_command")
    @patch("sys.stderr", new_callable=StringIO)
    def test_successful_movie_data_fetch(self, mock_stderr, mock_run_command):
        """Test successful fetching and parsing of movie data."""
        mock_movies = [
            {
                "title": "The Matrix",
                "runtime_minutes": 136,
                "year": 1999,
                "genres": ["Action", "Sci-Fi"],
                "rating": 8.7,
                "certification": "R",
            },
            {
                "title": "Inception",
                "runtime_minutes": 148,
                "year": 2010,
                "genres": ["Action", "Sci-Fi", "Thriller"],
                "rating": 8.8,
                "certification": "PG-13",
            },
        ]
        mock_run_command.return_value = json.dumps(mock_movies)

        result = get_movie_data()

        assert result == mock_movies
        assert len(result) == 2
        assert result[0]["title"] == "The Matrix"
        mock_run_command.assert_called_once_with(
            [
                "platelet-movie",
                "--format",
                "json",
                "--min-minutes",
                "90",
                "--max-minutes",
                "160",
                "--max-pages",
                "50",
                "--region",
                "US",
            ]
        )
        assert "Fetching movie data from TMDB for region US..." in mock_stderr.getvalue()

    @patch("generate_site_data.run_command")
    def test_invalid_json_raises_error(self, mock_run_command):
        """Test that invalid JSON response raises JSONDecodeError."""
        mock_run_command.return_value = "not valid json{"

        with pytest.raises(json.JSONDecodeError):
            get_movie_data()

    @patch("generate_site_data.run_command")
    def test_empty_json_array(self, mock_run_command):
        """Test handling of empty movie array."""
        mock_run_command.return_value = "[]"

        result = get_movie_data()

        assert result == []

    @patch("generate_site_data.run_command")
    def test_cli_command_failure_propagates(self, mock_run_command):
        """Test that CLI command failure is propagated."""
        mock_run_command.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["platelet-movie", "--format", "json"],
            stderr="API key missing",
        )

        with pytest.raises(subprocess.CalledProcessError):
            get_movie_data()

    @patch("generate_site_data.run_command")
    def test_custom_max_pages(self, mock_run_command):
        """Test that custom max_pages value is passed to CLI."""
        mock_run_command.return_value = "[]"

        get_movie_data(max_pages=10)

        mock_run_command.assert_called_once_with(
            [
                "platelet-movie",
                "--format",
                "json",
                "--min-minutes",
                "90",
                "--max-minutes",
                "160",
                "--max-pages",
                "10",
                "--region",
                "US",
            ]
        )

    @patch("generate_site_data.run_command")
    def test_max_pages_as_string(self, mock_run_command):
        """Test that max_pages can be passed as a string (e.g., from CLI args)."""
        mock_run_command.return_value = "[]"

        get_movie_data(max_pages="25")

        mock_run_command.assert_called_once_with(
            [
                "platelet-movie",
                "--format",
                "json",
                "--min-minutes",
                "90",
                "--max-minutes",
                "160",
                "--max-pages",
                "25",
                "--region",
                "US",
            ]
        )

    @patch("generate_site_data.run_command")
    def test_custom_region(self, mock_run_command):
        """Test that custom region value is passed to CLI."""
        mock_run_command.return_value = "[]"

        get_movie_data(region="GB")

        mock_run_command.assert_called_once_with(
            [
                "platelet-movie",
                "--format",
                "json",
                "--min-minutes",
                "90",
                "--max-minutes",
                "160",
                "--max-pages",
                "50",
                "--region",
                "GB",
            ]
        )


class TestGetCommentary:
    """Tests for get_commentary function."""

    @patch("subprocess.run")
    @patch("sys.stderr", new_callable=StringIO)
    def test_commentary_from_movie_list(self, mock_stderr, mock_subprocess_run):
        """Test generating commentary from a list of movie dicts."""
        mock_result = MagicMock()
        mock_result.stdout = "Dear Reader, what a delightful selection!"
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        movies = [
            {"title": "The Matrix", "runtime_minutes": 136, "year": 1999},
            {"title": "Inception", "runtime_minutes": 148, "year": 2010},
        ]

        result = get_commentary(movies)

        assert result == "Dear Reader, what a delightful selection!"
        assert "Generating Lady Whistledown commentary..." in mock_stderr.getvalue()

        # Verify the subprocess was called correctly
        call_args = mock_subprocess_run.call_args
        assert call_args[1]["input"].startswith("Movies:\n")
        assert "- The Matrix (136m, 1999)" in call_args[1]["input"]
        assert "- Inception (148m, 2010)" in call_args[1]["input"]
        assert call_args[1]["capture_output"] is True
        assert call_args[1]["text"] is True
        assert call_args[1]["check"] is True

    @patch("subprocess.run")
    def test_commentary_from_markdown_string(self, mock_subprocess_run):
        """Test generating commentary from a markdown string."""
        mock_result = MagicMock()
        mock_result.stdout = "Dear Reader, scandalous!"
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        markdown = "- The Matrix (136m, 1999)\n- Inception (148m, 2010)"

        result = get_commentary(markdown)

        assert result == "Dear Reader, scandalous!"

        # Verify the input was passed as-is
        call_args = mock_subprocess_run.call_args
        assert call_args[1]["input"] == markdown

    @patch("subprocess.run")
    def test_commentary_strips_trailing_whitespace(self, mock_subprocess_run):
        """Test that trailing whitespace is stripped from commentary."""
        mock_result = MagicMock()
        mock_result.stdout = "Commentary text\n\n  "
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        result = get_commentary([{"title": "Test", "runtime_minutes": 100, "year": 2020}])

        assert result == "Commentary text"

    @patch("subprocess.run")
    def test_commentary_handles_missing_movie_fields(self, mock_subprocess_run):
        """Test that missing movie fields use default values."""
        mock_result = MagicMock()
        mock_result.stdout = "Commentary"
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        movies = [
            {},  # All fields missing
            {"title": "Only Title"},  # Missing runtime and year
            {"runtime_minutes": 100},  # Missing title and year
        ]

        get_commentary(movies)

        call_args = mock_subprocess_run.call_args
        markdown_input = call_args[1]["input"]
        assert "- Unknown (?m, )" in markdown_input
        assert "- Only Title (?m, )" in markdown_input
        assert "- Unknown (100m, )" in markdown_input

    @patch("subprocess.run")
    def test_lady_whistledown_script_failure_raises(self, mock_subprocess_run):
        """Test that lady_whistledown.py failure raises exception."""
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["python", "lady_whistledown.py"],
            stderr="API error",
        )

        with pytest.raises(subprocess.CalledProcessError):
            get_commentary([{"title": "Test", "runtime_minutes": 100, "year": 2020}])


class TestGenerateSiteData:
    """Tests for generate_site_data function."""

    @patch("generate_site_data.get_movie_data")
    @patch("generate_site_data.get_commentary")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    @patch("sys.stderr", new_callable=StringIO)
    @patch("generate_site_data.datetime")
    def test_successful_site_data_generation(
        self,
        mock_datetime,
        mock_stderr,
        mock_mkdir,
        mock_file,
        mock_get_commentary,
        mock_get_movie_data,
    ):
        """Test successful generation of site data JSON."""
        # Mock current time
        mock_now = datetime(2026, 4, 14, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        # Mock movie data
        mock_movies = [
            {"title": "The Matrix", "runtime_minutes": 136, "year": 1999},
            {"title": "Inception", "runtime_minutes": 148, "year": 2010},
        ]
        mock_get_movie_data.return_value = mock_movies

        # Mock commentary
        mock_get_commentary.return_value = "Dear Reader, what a selection!"

        # Run the function
        generate_site_data()

        # Verify get_movie_data was called
        mock_get_movie_data.assert_called_once()

        # Verify get_commentary was called with correct markdown
        mock_get_commentary.assert_called_once()
        commentary_arg = mock_get_commentary.call_args[0][0]
        assert "- The Matrix (136m, 1999)" in commentary_arg
        assert "- Inception (148m, 2010)" in commentary_arg

        # Verify directory creation
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # Verify file writing
        mock_file.assert_called_once()
        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        site_data = json.loads(written_data)

        assert site_data["generated_at"] == "2026-04-14T12:00:00+00:00"
        assert site_data["commentary"] == "Dear Reader, what a selection!"
        assert site_data["movies"] == mock_movies
        assert len(site_data["movies"]) == 2

        # Verify success message
        assert "✓ Generated" in mock_stderr.getvalue()
        assert "2 movies" in mock_stderr.getvalue()

    @patch("generate_site_data.get_movie_data")
    @patch("sys.stderr", new_callable=StringIO)
    def test_movie_data_fetch_failure_exits(self, mock_stderr, mock_get_movie_data):
        """Test that movie data fetch failure causes exit with code 1."""
        mock_get_movie_data.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["platelet-movie", "--format", "json"],
            stderr="TMDB API error",
        )

        with pytest.raises(SystemExit) as exc_info:
            generate_site_data()

        assert exc_info.value.code == 1
        assert "Error: Failed to generate site data" in mock_stderr.getvalue()

    @patch("generate_site_data.get_movie_data")
    @patch("sys.stderr", new_callable=StringIO)
    def test_json_decode_error_exits(self, mock_stderr, mock_get_movie_data):
        """Test that JSON decode error causes exit with code 1."""
        mock_get_movie_data.side_effect = json.JSONDecodeError(
            "Expecting value", "doc", 0
        )

        with pytest.raises(SystemExit) as exc_info:
            generate_site_data()

        assert exc_info.value.code == 1
        assert "Error: Invalid JSON in response" in mock_stderr.getvalue()

    @patch("generate_site_data.get_movie_data")
    @patch("generate_site_data.get_commentary")
    @patch("sys.stderr", new_callable=StringIO)
    def test_unexpected_error_exits(self, mock_stderr, mock_get_commentary, mock_get_movie_data):
        """Test that unexpected errors cause exit with code 1."""
        mock_get_movie_data.return_value = [
            {"title": "Test", "runtime_minutes": 100, "year": 2020}
        ]
        mock_get_commentary.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(SystemExit) as exc_info:
            generate_site_data()

        assert exc_info.value.code == 1
        assert "Error: Unexpected error during site generation" in mock_stderr.getvalue()

    @patch("generate_site_data.get_movie_data")
    @patch("generate_site_data.get_commentary")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    @patch("sys.stderr", new_callable=StringIO)
    def test_handles_empty_movie_list(
        self,
        mock_stderr,
        mock_mkdir,
        mock_file,
        mock_get_commentary,
        mock_get_movie_data,
    ):
        """Test handling of empty movie list."""
        mock_get_movie_data.return_value = []
        mock_get_commentary.return_value = "Dear Reader, alas, no movies!"

        generate_site_data()

        # Verify empty movie list is handled
        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        site_data = json.loads(written_data)

        assert site_data["movies"] == []
        assert "0 movies" in mock_stderr.getvalue()

    @patch("generate_site_data.get_movie_data")
    @patch("generate_site_data.get_commentary")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_handles_movie_dict_with_movies_key(
        self,
        mock_mkdir,
        mock_file,
        mock_get_commentary,
        mock_get_movie_data,
    ):
        """Test handling when get_movie_data returns dict with 'movies' key."""
        mock_movies = [
            {"title": "Test Movie", "runtime_minutes": 100, "year": 2020}
        ]
        mock_get_movie_data.return_value = {"movies": mock_movies, "total": 1}
        mock_get_commentary.return_value = "Commentary"

        generate_site_data()

        # Verify movies are extracted from dict
        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        site_data = json.loads(written_data)

        assert site_data["movies"] == mock_movies
