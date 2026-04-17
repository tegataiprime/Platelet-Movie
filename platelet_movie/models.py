"""Movie data model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(order=False)
class Movie:
    """Represents a single Netflix movie entry."""

    title: str
    runtime_minutes: int
    genres: list[str] = field(default_factory=list)
    rating: float | None = None
    certification: str | None = None  # MPAA rating (R, PG-13, PG, G, etc.)
    year: int | None = None  # Release year
    description: str | None = None  # Movie description/overview from TMDB
    poster_url: str | None = None  # URL to movie poster image from TMDB

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Movie):
            return NotImplemented
        return (self.runtime_minutes, self.title.lower()) < (
            other.runtime_minutes,
            other.title.lower(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Movie):
            return NotImplemented
        return (
            self.title == other.title
            and self.runtime_minutes == other.runtime_minutes
            and self.genres == other.genres
            and self.rating == other.rating
            and self.certification == other.certification
            and self.year == other.year
            and self.description == other.description
            and self.poster_url == other.poster_url
        )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Movie(title={self.title!r}, runtime_minutes={self.runtime_minutes}, "
            f"genres={self.genres!r}, rating={self.rating}, "
            f"certification={self.certification!r}, year={self.year}, "
            f"description={self.description!r}, poster_url={self.poster_url!r})"
        )
