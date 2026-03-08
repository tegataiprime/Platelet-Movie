"""Command-line interface for Platelet-Movie."""

from __future__ import annotations

import sys

import click

from platelet_movie.client import NetflixClient
from platelet_movie.config import Config

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
    "--api-key",
    envvar="NETFLIX_API_KEY",
    default=None,
    help="Netflix search API key (overrides NETFLIX_API_KEY env var).",
)
@click.option(
    "--api-host",
    envvar="NETFLIX_API_HOST",
    default=None,
    help="Netflix search API host (overrides NETFLIX_API_HOST env var).",
)
@click.version_option(package_name="platelet-movie")
def main(
    min_minutes: int,
    email: str | None,
    password: str | None,
    api_key: str | None,
    api_host: str | None,
) -> None:
    """Discover Netflix movies long enough for a Platelet Donation.

    Queries Netflix for movies with a runtime >= MIN_MINUTES (default: 135)
    and prints the results sorted by runtime then title, ascending.

    All credentials can be supplied via environment variables or CLI flags:

    \b
        NETFLIX_EMAIL      – your Netflix account e-mail
        NETFLIX_PASSWORD   – your Netflix account password
        NETFLIX_API_KEY    – RapidAPI key for the uNoGS endpoint
        NETFLIX_API_HOST   – uNoGS API host (optional, has a default)
    """
    config = Config(
        netflix_email=email,
        netflix_password=password,
        api_host=api_host,
        api_key=api_key,
    )

    try:
        config.validate()
    except ValueError as exc:
        click.echo(f"Configuration error: {exc}", err=True)
        sys.exit(1)

    client = NetflixClient(config)

    try:
        movies = client.get_movies(min_minutes=min_minutes)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error querying Netflix API: {exc}", err=True)
        sys.exit(1)

    if not movies:
        click.echo(f"No movies found with a runtime of at least {min_minutes} minutes.")
        return

    click.echo(f"Netflix movies with a runtime >= {min_minutes} minutes:\n")
    click.echo(f"{'Runtime':>10}  Title")
    click.echo("-" * 60)
    for movie in movies:
        click.echo(f"{movie.runtime_minutes:>8} m  {movie.title}")
