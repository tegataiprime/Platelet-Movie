"""Command-line interface for Platelet-Movie."""

from __future__ import annotations

import logging
import sys

import click

from platelet_movie.config import Config
from platelet_movie.tmdb_client import TMDBAPIError, TMDBClient

logger = logging.getLogger(__name__)

_DEFAULT_MIN_MINUTES = 135
_DEFAULT_MAX_MINUTES = 145
_DEFAULT_LANGUAGE = "en"


@click.command()
@click.option(
    "--min-minutes",
    default=_DEFAULT_MIN_MINUTES,
    show_default=True,
    type=click.IntRange(min=0),
    help="Minimum movie runtime in minutes.",
)
@click.option(
    "--max-minutes",
    default=_DEFAULT_MAX_MINUTES,
    show_default=True,
    type=click.IntRange(min=1),
    help="Maximum movie runtime in minutes.",
)
@click.option(
    "--language",
    default=_DEFAULT_LANGUAGE,
    show_default=True,
    help="Original language filter (ISO 639-1 code, e.g., 'en' for English).",
)
@click.option(
    "--max-pages",
    default=None,
    type=click.IntRange(min=1, max=500),
    help="Maximum number of TMDB result pages to fetch (20 movies per page). Default: 10.",
)
@click.option(
    "--api-key",
    envvar="TMDB_API_KEY",
    default=None,
    help="TMDB API key (overrides TMDB_API_KEY env var).",
)
@click.option(
    "--region",
    envvar="TMDB_REGION",
    default=None,
    help="Netflix region code (e.g., US, GB). Default: US.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Enable verbose debug logging.",
)
@click.version_option(package_name="platelet-movie")
def main(
    min_minutes: int,
    max_minutes: int,
    language: str,
    max_pages: int | None,
    api_key: str | None,
    region: str | None,
    verbose: bool,
) -> None:
    """Discover Netflix movies long enough for a Platelet Donation.

    Uses the TMDB (The Movie Database) API to find movies available on Netflix
    whose runtime is >= MIN_MINUTES.  Results are sorted by runtime then title,
    ascending.

    All credentials and tuning parameters can be supplied via environment
    variables or CLI flags:

    \b
        TMDB_API_KEY    – your TMDB API key (free at themoviedb.org)
        TMDB_REGION     – Netflix region code, e.g., US, GB (default: US)
        TMDB_MAX_PAGES  – max result pages to fetch, 20 movies/page (default: 10)
    """
    # Configure logging
    # Only output logs to stderr when --verbose is set
    # This prevents log messages from appearing in stdout (e.g., email reports)
    root_logger = logging.getLogger()
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    if verbose:
        # Set up debug logging to stderr
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.DEBUG)
    else:
        # When not verbose, suppress all logging to keep stdout clean
        # Use NullHandler to avoid "No handlers could be found" warnings
        root_logger.addHandler(logging.NullHandler())
        root_logger.setLevel(logging.CRITICAL + 1)  # Silence all logs

    logger.debug("Starting Platelet-Movie CLI")
    logger.debug(
        f"Arguments: min_minutes={min_minutes}, max_minutes={max_minutes}, "
        f"language={language}, max_pages={max_pages}, region={region}, verbose={verbose}"
    )

    config = Config(
        tmdb_api_key=api_key,
        tmdb_region=region,
        max_pages=max_pages,
    )

    try:
        config.validate()
        logger.debug("Configuration validated successfully")
        logger.debug(f"Config: region={config.tmdb_region}, max_pages={config.max_pages}")
    except ValueError as exc:
        logger.error(f"Configuration validation failed: {exc}")
        click.echo(f"Configuration error: {exc}", err=True)
        sys.exit(1)

    client = TMDBClient(
        api_key=config.tmdb_api_key, region=config.tmdb_region, max_pages=config.max_pages
    )
    logger.debug("TMDBClient initialized")

    try:
        runtime_msg = f"minimum runtime of {min_minutes} minutes"
        if max_minutes:
            runtime_msg = f"runtime between {min_minutes} and {max_minutes} minutes"
        logger.info(f"Discovering movies with {runtime_msg}")
        movies = client.discover_movies_on_netflix(
            min_runtime_minutes=min_minutes,
            max_runtime_minutes=max_minutes,
            language=language,
        )
        logger.info(f"Discovery completed. Found {len(movies)} matching movies")
    except TMDBAPIError as exc:
        logger.error(f"TMDB API error: {exc}", exc_info=verbose)
        click.echo(f"Error querying TMDB API: {exc}", err=True)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Unexpected error: {exc}", exc_info=verbose)
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if not movies:
        logger.info("No movies found matching criteria")
        runtime_msg = f"at least {min_minutes} minutes"
        if max_minutes:
            runtime_msg = f"between {min_minutes} and {max_minutes} minutes"
        click.echo(f"No movies found with a runtime of {runtime_msg}.")
        return

    logger.debug(f"Displaying {len(movies)} movies")
    runtime_header = f">= {min_minutes} minutes"
    if max_minutes:
        runtime_header = f"{min_minutes}-{max_minutes} minutes"
    click.echo(f"Netflix movies with a runtime {runtime_header}:\n")
    click.echo(f"{'Runtime':>10}  {'Score':>6}  {'Rated':<7}  {'Genres':<20}  Title")
    click.echo("-" * 85)
    for movie in movies:
        rating_str = f"{movie.rating:.1f}" if movie.rating is not None else "N/A"
        cert_str = movie.certification if movie.certification else "NR"
        genres_str = ", ".join(movie.genres[:2]) if movie.genres else "N/A"
        # Truncate genres if too long
        if len(genres_str) > 20:
            genres_str = genres_str[:17] + "..."
        click.echo(
            f"{movie.runtime_minutes:>8} m  {rating_str:>6}  {cert_str:<7}  "
            f"{genres_str:<20}  {movie.title}"
        )
