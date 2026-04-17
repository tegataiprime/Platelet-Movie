"""Movie list formatters for various output formats."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from platelet_movie.models import Movie

FormatType = Literal["markdown", "html", "csv", "json"]


def _get_description_str(description: str | None) -> str:
    """Get description string for display, returning 'N/A' for None values."""
    return description if description is not None else "N/A"


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
    """Format movies as a GFM pipe table."""
    if not movies:
        return ""

    lines = []
    lines.append(
        f"| {'Runtime':>10} | {'Year':>6} | {'Score':>6} | {'Rated':<7} | {'Genres':<20} | Title | Description |"
    )
    lines.append(f"| {'---':>10} | {'---':>6} | {'---':>6} | {'---':<7} | {'---':<20} | --- | --- |")

    for movie in movies:
        rating_str = f"{movie.rating:.1f}" if movie.rating is not None else "N/A"
        cert_str = movie.certification if movie.certification else "NR"
        year_str = str(movie.year) if movie.year is not None else "N/A"
        genres_str = ", ".join(movie.genres[:2]) if movie.genres else "N/A"
        # Truncate genres if too long
        if len(genres_str) > 20:
            genres_str = genres_str[:17] + "..."
        desc_str = _get_description_str(movie.description)
        lines.append(
            f"| {movie.runtime_minutes:>8} m | {year_str:>6} | {rating_str:>6} | {cert_str:<7} | "
            f"{genres_str:<20} | {movie.title} | {desc_str} |"
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
    html_parts.append("      <th>Year</th>")
    html_parts.append("      <th>Score</th>")
    html_parts.append("      <th>Rated</th>")
    html_parts.append("      <th>Genres</th>")
    html_parts.append("      <th>Title</th>")
    html_parts.append("      <th>Description</th>")
    html_parts.append("    </tr>")
    html_parts.append("  </thead>")
    html_parts.append("  <tbody>")

    for movie in movies:
        rating_str = f"{movie.rating:.1f}" if movie.rating is not None else "N/A"
        cert_str = movie.certification if movie.certification else "NR"
        year_str = str(movie.year) if movie.year is not None else "N/A"
        genres_str = ", ".join(movie.genres) if movie.genres else "N/A"
        desc_str = _get_description_str(movie.description)

        html_parts.append("    <tr>")
        html_parts.append(f"      <td>{movie.runtime_minutes} min</td>")
        html_parts.append(f"      <td>{year_str}</td>")
        html_parts.append(f"      <td>{rating_str}</td>")
        html_parts.append(f"      <td>{cert_str}</td>")
        html_parts.append(f"      <td>{genres_str}</td>")
        html_parts.append(f"      <td>{movie.title}</td>")
        html_parts.append(f"      <td>{desc_str}</td>")
        html_parts.append("    </tr>")

    html_parts.append("  </tbody>")
    html_parts.append("</table>")

    return "\n".join(html_parts)


def _format_csv(movies: list[Movie]) -> str:
    """Format movies as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["Runtime", "Year", "Score", "Rated", "Genres", "Title", "Description"])

    # Write data rows
    for movie in movies:
        rating_str = f"{movie.rating:.1f}" if movie.rating is not None else "N/A"
        cert_str = movie.certification if movie.certification else "NR"
        year_str = str(movie.year) if movie.year is not None else "N/A"
        genres_str = ", ".join(movie.genres) if movie.genres else "N/A"
        desc_str = _get_description_str(movie.description)

        writer.writerow(
            [
                f"{movie.runtime_minutes} min",
                year_str,
                rating_str,
                cert_str,
                genres_str,
                movie.title,
                desc_str,
            ]
        )

    return output.getvalue()


def _format_json(movies: list[Movie]) -> str:
    """Format movies as JSON."""
    movie_dicts = [
        {
            "title": movie.title,
            "runtime_minutes": movie.runtime_minutes,
            "year": movie.year,
            "genres": movie.genres,
            "vote_average": movie.rating,
            "certification": movie.certification,
            "description": movie.description,
        }
        for movie in movies
    ]
    return json.dumps(movie_dicts, indent=2)
