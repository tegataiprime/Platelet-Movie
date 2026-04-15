#!/usr/bin/env python3
"""Generate data.json for the static website."""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_command(cmd: list[str]) -> str:
    """Run a command and return its output.

    Args:
        cmd: Command and arguments as list

    Returns:
        Command output as string

    Raises:
        subprocess.CalledProcessError: If command fails
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(cmd)}: {e.stderr}", file=sys.stderr)
        raise


def get_movie_data(max_pages: int | str = 50, region: str = "US") -> dict:
    """Get movie data from platelet-movie CLI.

    Args:
        max_pages: Maximum number of pages to fetch from TMDB (default: 50)
        region: Netflix region code (e.g., US, GB, IN) (default: US)

    Returns:
        Parsed JSON data with movies

    Raises:
        subprocess.CalledProcessError: If CLI fails
        json.JSONDecodeError: If output is not valid JSON
    """
    print(f"Fetching movie data from TMDB for region {region}...", file=sys.stderr)
    # Use the installed entry point instead of -m
    output = run_command(
        [
            "platelet-movie",
            "--format",
            "json",
            "--min-minutes",
            "90",
            "--max-minutes",
            "160",
            "--max-pages",
            str(max_pages),
            "--region",
            region,
        ]
    )
    return json.loads(output)


def get_commentary(movie_data: list[dict] | str) -> str:
    """Get Lady Whistledown commentary for the movies.

    Args:
        movie_data: Either a list of movie dicts or a markdown string

    Returns:
        Lady Whistledown commentary

    Raises:
        subprocess.CalledProcessError: If lady_whistledown.py fails
    """
    print("Generating Lady Whistledown commentary...", file=sys.stderr)

    # Format movies as markdown for the lady_whistledown script
    if isinstance(movie_data, str):
        # Already in markdown format
        markdown_movies = movie_data
    else:
        # Convert list of movies to markdown
        markdown_movies = "Movies:\n"
        for movie in movie_data:
            title = movie.get("title", "Unknown")
            runtime = movie.get("runtime_minutes", "?")
            year = movie.get("year", "")
            markdown_movies += f"- {title} ({runtime}m, {year})\n"

    # Run lady_whistledown script
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "lady_whistledown.py")],
        input=markdown_movies,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def prepare_site_data(movies: list[dict], commentary: str, region_code: str) -> dict:
    """Prepare the site data structure.

    Args:
        movies: List of movie dictionaries or dict with movies key
        commentary: Lady Whistledown commentary
        region_code: Region code for the data

    Returns:
        Dictionary with site data structure
    """
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "region": region_code,
        "commentary": commentary,
        "movies": movies if isinstance(movies, list) else movies.get("movies", []),
    }


def save_site_data(site_data: dict, region_code: str) -> Path:
    """Save site data to JSON file.

    Args:
        site_data: Site data dictionary
        region_code: Region code for filename

    Returns:
        Path to saved file
    """
    output_filename = f"data-{region_code.lower()}.json"
    output_path = Path(__file__).parent.parent / "site" / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(site_data, f, indent=2)

    return output_path


def generate_region_data(max_pages: int, region_code: str) -> None:
    """Generate site data for a single region.

    Args:
        max_pages: Maximum number of pages to fetch from TMDB
        region_code: Region code to generate data for

    Raises:
        subprocess.CalledProcessError: If CLI fails
        json.JSONDecodeError: If output is not valid JSON
        Exception: For other unexpected errors
    """
    print(f"\n{'=' * 60}", file=sys.stderr)
    print(f"Generating data for region: {region_code}", file=sys.stderr)
    print(f"{'=' * 60}", file=sys.stderr)

    # Get movie data
    movies = get_movie_data(max_pages=max_pages, region=region_code)

    # Get commentary
    movie_markdown = "\n".join(
        f"- {m.get('title', 'Unknown')} ({m.get('runtime_minutes', '?')}m, {m.get('year', '')})"
        for m in (movies if isinstance(movies, list) else [])
    )
    commentary = get_commentary(movie_markdown)

    # Prepare and save data
    site_data = prepare_site_data(movies, commentary, region_code)
    output_path = save_site_data(site_data, region_code)

    print(f"✓ Generated {output_path} with {len(site_data['movies'])} movies", file=sys.stderr)


def handle_generation_error(error: Exception, region_code: str, is_single_region: bool) -> None:
    """Handle errors during data generation.

    Args:
        error: The exception that occurred
        region_code: Region code being processed
        is_single_region: Whether generating for a specific region only
    """
    if isinstance(error, subprocess.CalledProcessError):
        message = f"Error: Failed to generate site data for region {region_code}: {error}"
    elif isinstance(error, json.JSONDecodeError):
        message = f"Error: Invalid JSON in response for region {region_code}: {error}"
    else:
        message = (
            f"Error: Unexpected error during site generation for region {region_code}: {error}"
        )

    print(message, file=sys.stderr)

    if is_single_region:
        sys.exit(1)


def generate_site_data(max_pages: int = 50, region: str | None = None) -> None:
    """Generate and save site/data-{region}.json with movie data and commentary.

    Args:
        max_pages: Maximum number of pages to fetch from TMDB (default: 50)
        region: Netflix region code (e.g., US, GB, IN). If None, generates
            for all supported regions.
    """
    # Define supported regions
    supported_regions = ["US", "GB", "IN"]
    regions_to_generate = [region.upper()] if region is not None else supported_regions
    is_single_region = region is not None

    for region_code in regions_to_generate:
        try:
            generate_region_data(max_pages, region_code)
        except subprocess.CalledProcessError as e:
            handle_generation_error(e, region_code, is_single_region)
        except json.JSONDecodeError as e:
            handle_generation_error(e, region_code, is_single_region)
        except Exception as e:
            handle_generation_error(e, region_code, is_single_region)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Generate data-{region}.json files for the static website "
            "with movie data and commentary."
        )
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="Maximum number of pages to fetch from TMDB (default: 50)",
    )
    parser.add_argument(
        "--region",
        type=str,
        default=None,
        help=(
            "Netflix region code (e.g., US, GB, IN). If not specified, "
            "generates for all supported regions (US, GB, IN)."
        ),
    )
    args = parser.parse_args()
    generate_site_data(max_pages=args.max_pages, region=args.region)
