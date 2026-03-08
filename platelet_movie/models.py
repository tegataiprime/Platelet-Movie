"""Movie data model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(order=False)
class Movie:
    """Represents a single Netflix movie entry."""

    title: str
    runtime_minutes: int

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
        return self.title == other.title and self.runtime_minutes == other.runtime_minutes

    def __repr__(self) -> str:  # pragma: no cover
        return f"Movie(title={self.title!r}, runtime_minutes={self.runtime_minutes})"
