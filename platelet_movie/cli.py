"""Command-line interface for Platelet-Movie."""

from __future__ import annotations

import sys

import click

from platelet_movie.config import Config
from platelet_movie.scraper import NetflixScraper

_DEFAULT_MIN_MINUTES = 135


@click.command()
@click.option(
    "--min-minutes",
    default=_DEFAULT_MIN_MINUTES,
    show_default=True,
    type=click.IntRange(min=0),
    help="Minimum movie runtime in minutes.",
)
@click.option(
    "--email",
    envvar="NETFLIX_EMAIL",
    default=None,
    help="Netflix account e-mail (overrides NETFLIX_EMAIL env var).",
)
@click.option(
    "--password",
    envvar="NETFLIX_PASSWORD",
    default=None,
    help="Netflix account password (overrides NETFLIX_PASSWORD env var).",
)
@click.option(
    "--no-headless",
    is_flag=True,
    default=False,
    help="Show the browser window (useful for debugging login issues).",
)
@click.option(
    "--request-delay",
    envvar="NETFLIX_REQUEST_DELAY_S",
    default=None,
    type=float,
    help="Seconds to wait between page loads (default: 2.0).",
)
@click.option(
    "--max-movies",
    envvar="NETFLIX_MAX_MOVIES",
    default=None,
    type=int,
    help="Maximum number of movies to inspect per session (default: 100).",
)
@click.version_option(package_name="platelet-movie")
def main(
    min_minutes: int,
    email: str | None,
    password: str | None,
    no_headless: bool,
    request_delay: float | None,
    max_movies: int | None,
) -> None:
    """Discover Netflix movies long enough for a Platelet Donation.

    Uses a real Chromium browser (via Playwright) to log in to Netflix and
    scrape movies whose runtime is >= MIN_MINUTES.  Results are sorted by
    runtime then title, ascending.

    All credentials and tuning parameters can be supplied via environment
    variables or CLI flags:

    \b
        NETFLIX_EMAIL              – your Netflix account e-mail
        NETFLIX_PASSWORD           – your Netflix account password
        NETFLIX_HEADLESS           – 1/true/yes to run headless (default: 1)
        NETFLIX_REQUEST_DELAY_S    – seconds between page loads (default: 2.0)
        NETFLIX_MAX_MOVIES         – max movies per session (default: 100)
        NETFLIX_PAGE_TIMEOUT_MS    – page load timeout in ms (default: 30000)
    """
    # --no-headless flag overrides env var; otherwise Config reads NETFLIX_HEADLESS
    headless_override: bool | None = False if no_headless else None

    config = Config(
        netflix_email=email,
        netflix_password=password,
        headless=headless_override,
        request_delay_s=request_delay,
        max_movies=max_movies,
    )

    try:
        config.validate()
    except ValueError as exc:
        click.echo(f"Configuration error: {exc}", err=True)
        sys.exit(1)

    scraper = NetflixScraper(config)

    try:
        movies = scraper.get_movies(min_minutes=min_minutes)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error scraping Netflix: {exc}", err=True)
        sys.exit(1)

    if not movies:
        click.echo(f"No movies found with a runtime of at least {min_minutes} minutes.")
        return

    click.echo(f"Netflix movies with a runtime >= {min_minutes} minutes:\n")
    click.echo(f"{'Runtime':>10}  Title")
    click.echo("-" * 60)
    for movie in movies:
        click.echo(f"{movie.runtime_minutes:>8} m  {movie.title}")
