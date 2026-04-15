"""Unit tests for platelet_movie.formatters."""

import pytest
import re

from platelet_movie.formatters import format_movies
from platelet_movie.models import Movie


class TestFormatters:
    """Test suite for movie list formatters."""

    def setup_method(self):
        """Set up test data."""
        self.movies = [
            Movie(
                title="The Irishman",
                runtime_minutes=135,
                genres=["Crime", "Drama"],
                rating=8.1,
                certification="R",
                year=2019,
            ),
            Movie(
                title="Interstellar",
                runtime_minutes=142,
                genres=["Drama", "Mystery"],
                rating=8.5,
                certification="PG-13",
                year=2014,
            ),
            Movie(
                title="Basic Movie",
                runtime_minutes=140,
                genres=[],
                rating=None,
                certification=None,
                year=None,
            ),
        ]

    def test_format_markdown(self):
        """Test markdown table formatting."""
        result = format_movies(self.movies, "markdown")
        assert "Runtime" in result
        assert "Score" in result
        assert "Rated" in result
        assert "Genres" in result
        assert "Title" in result
        assert "Year" in result
        assert "The Irishman" in result
        assert "135" in result
        assert "8.1" in result
        assert "R" in result
        assert "2019" in result
        assert "2014" in result
        assert "Crime, Drama" in result
        # Check that it's formatted as a table with separators
        assert "-" in result

    def test_format_markdown_uses_pipe_table_syntax(self):
        """Test that markdown output uses GFM pipe table syntax."""
        result = format_movies(self.movies, "markdown")
        lines = result.splitlines()
        # Header row must start and end with a pipe character
        header_line = lines[0]
        assert header_line.startswith("|"), "Header row must start with '|'"
        assert header_line.endswith("|"), "Header row must end with '|'"
        # Second line must be the separator row (dashes between pipes)
        separator_line = lines[1]
        assert separator_line.startswith("|"), "Separator row must start with '|'"
        assert separator_line.endswith("|"), "Separator row must end with '|'"
        assert "---" in separator_line, "Separator row must contain '---'"
        # Every pipe in the separator row must be followed by dashes or colons (spaces allowed)
        assert re.search(r"\|\s*[-:]+\s*\|", separator_line), "Separator must have |---|"
        # Data rows must also use pipe syntax
        for line in lines[2:]:
            assert line.startswith("|"), f"Data row must start with '|': {line!r}"
            assert line.endswith("|"), f"Data row must end with '|': {line!r}"

    def test_format_html(self):
        """Test HTML table formatting."""
        result = format_movies(self.movies, "html")
        assert "<table" in result
        assert "<tr>" in result
        assert "<th>" in result
        assert "<td>" in result
        assert "</table>" in result
        assert "The Irishman" in result
        assert "135" in result
        assert "8.1" in result
        assert "2019" in result

    def test_format_csv(self):
        """Test CSV formatting."""
        result = format_movies(self.movies, "csv")
        lines = result.strip().split("\n")
        # Should have header + 3 movies = 4 lines
        assert len(lines) == 4
        # Check header
        assert "Runtime" in lines[0]
        assert "Score" in lines[0]
        assert "Title" in lines[0]
        assert "Year" in lines[0]
        # Check data
        assert "The Irishman" in result
        assert "135" in result
        assert "8.1" in result
        assert "2019" in result

    def test_format_json(self):
        """Test JSON formatting."""
        import json

        result = format_movies(self.movies, "json")
        # Should be valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 3
        # Check first movie
        assert parsed[0]["title"] == "The Irishman"
        assert parsed[0]["runtime_minutes"] == 135
        assert parsed[0]["vote_average"] == pytest.approx(8.1)
        assert parsed[0]["certification"] == "R"
        assert parsed[0]["year"] == 2019
        assert "Crime" in parsed[0]["genres"]

    def test_format_handles_none_values(self):
        """Test that formatters handle None values gracefully."""
        movies = [Movie(title="Test", runtime_minutes=100, rating=None, certification=None)]

        # Markdown
        md_result = format_movies(movies, "markdown")
        assert "N/A" in md_result or "NR" in md_result

        # HTML
        html_result = format_movies(movies, "html")
        assert "N/A" in html_result or "NR" in html_result

        # CSV - should contain N/A for None values
        csv_result = format_movies(movies, "csv")
        assert "N/A" in csv_result

        # JSON (None should be preserved in JSON)
        import json

        json_result = format_movies(movies, "json")
        parsed = json.loads(json_result)
        assert parsed[0]["vote_average"] is None
        assert parsed[0]["certification"] is None

    def test_format_empty_list(self):
        """Test formatting empty movie list."""
        result = format_movies([], "markdown")
        # Should return empty string or minimal structure
        assert isinstance(result, str)

    def test_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        import pytest

        with pytest.raises(ValueError):
            format_movies(self.movies, "invalid_format")

    def test_html_format_proper_structure(self):
        """Test that HTML output has proper table structure."""
        result = format_movies(self.movies, "html")
        # Should have proper HTML table tags
        assert result.count("<table") == 1
        assert result.count("</table>") == 1
        # Should have header row
        assert "<thead>" in result or "<th>" in result
        # Should have body rows
        assert result.count("<tr>") >= len(self.movies) + 1  # +1 for header

    def test_csv_escapes_special_characters(self):
        """Test that CSV properly escapes commas and quotes in fields."""
        movies = [
            Movie(
                title='Movie with, comma "and" quotes',
                runtime_minutes=150,
                genres=["Action", "Drama"],
            )
        ]
        result = format_movies(movies, "csv")
        # CSV should properly quote the title field containing commas and quotes
        # Parse the CSV to verify proper escaping
        import csv
        import io

        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        # Should have header + 1 data row
        assert len(rows) == 2
        # The title should be in the last column and properly preserved
        assert rows[1][-1] == 'Movie with, comma "and" quotes'

    def test_json_preserves_all_fields(self):
        """Test that JSON output includes all movie fields."""
        import json

        result = format_movies(self.movies, "json")
        parsed = json.loads(result)
        first_movie = parsed[0]
        # Should have all fields
        assert "title" in first_movie
        assert "runtime_minutes" in first_movie
        assert "genres" in first_movie
        assert "vote_average" in first_movie
        assert "certification" in first_movie
        assert "year" in first_movie
