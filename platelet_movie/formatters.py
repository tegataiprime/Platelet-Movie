"""Movie list formatters for various output formats."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from platelet_movie.models import Movie

FormatType = Literal["markdown", "html", "csv", "json"]


def format_movies(movies: list[Movie], format_type: FormatType) -> str:
    """Format a list of movies in the specified format.

    Args:
        movies: List of Movie objects to format
        format_type: Output format (markdown, html, csv, or json)

    Returns:
        Formatted string representation of the movie list

    Raises:
        ValueError: If format_type is not supported
    """
    if format_type == "markdown":
        return _format_markdown(movies)
    elif format_type == "html":
        return _format_html(movies)
    elif format_type == "csv":
        return _format_csv(movies)
    elif format_type == "json":
        return _format_json(movies)
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def _format_markdown(movies: list[Movie]) -> str:
    """Format movies as a markdown table."""
    if not movies:
        return ""

    lines = []
    lines.append(f"{'Runtime':>10}  {'Score':>6}  {'Rated':<7}  {'Genres':<20}  Title")
    lines.append("-" * 85)

    for movie in movies:
        rating_str = f"{movie.rating:.1f}" if movie.rating is not None else "N/A"
        cert_str = movie.certification if movie.certification else "NR"
        genres_str = ", ".join(movie.genres[:2]) if movie.genres else "N/A"
        # Truncate genres if too long
        if len(genres_str) > 20:
            genres_str = genres_str[:17] + "..."
        lines.append(
            f"{movie.runtime_minutes:>8} m  {rating_str:>6}  {cert_str:<7}  "
            f"{genres_str:<20}  {movie.title}"
        )

    return "\n".join(lines)


def _format_html(movies: list[Movie]) -> str:
    """Format movies as an HTML table."""
    if not movies:
        return "<table></table>"

    html_parts = ['<table border="1" cellpadding="5" cellspacing="0">']
    html_parts.append("  <thead>")
    html_parts.append("    <tr>")
    html_parts.append("      <th>Runtime</th>")
    html_parts.append("      <th>Score</th>")
    html_parts.append("      <th>Rated</th>")
    html_parts.append("      <th>Genres</th>")
    html_parts.append("      <th>Title</th>")
    html_parts.append("    </tr>")
    html_parts.append("  </thead>")
    html_parts.append("  <tbody>")

    for movie in movies:
        rating_str = f"{movie.rating:.1f}" if movie.rating is not None else "N/A"
        cert_str = movie.certification if movie.certification else "NR"
        genres_str = ", ".join(movie.genres) if movie.genres else "N/A"

        html_parts.append("    <tr>")
        html_parts.append(f"      <td>{movie.runtime_minutes} min</td>")
        html_parts.append(f"      <td>{rating_str}</td>")
        html_parts.append(f"      <td>{cert_str}</td>")
        html_parts.append(f"      <td>{genres_str}</td>")
        html_parts.append(f"      <td>{movie.title}</td>")
        html_parts.append("    </tr>")

    html_parts.append("  </tbody>")
    html_parts.append("</table>")

    return "\n".join(html_parts)


def _format_csv(movies: list[Movie]) -> str:
    """Format movies as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["Runtime", "Score", "Rated", "Genres", "Title"])

    # Write data rows
    for movie in movies:
        rating_str = f"{movie.rating:.1f}" if movie.rating is not None else "N/A"
        cert_str = movie.certification if movie.certification else "NR"
        genres_str = ", ".join(movie.genres) if movie.genres else "N/A"

        writer.writerow(
            [f"{movie.runtime_minutes} min", rating_str, cert_str, genres_str, movie.title]
        )

    return output.getvalue()


def _format_json(movies: list[Movie]) -> str:
    """Format movies as JSON."""
    movie_dicts = [
        {
            "title": movie.title,
            "runtime_minutes": movie.runtime_minutes,
            "genres": movie.genres,
            "rating": movie.rating,
            "certification": movie.certification,
        }
        for movie in movies
    ]
    return json.dumps(movie_dicts, indent=2)
