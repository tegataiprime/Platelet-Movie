"""Unit tests for platelet_movie.models."""

import pytest

from platelet_movie.models import Movie


class TestMovie:
    def test_creation(self):
        m = Movie(title="Inception", runtime_minutes=148)
        assert m.title == "Inception"
        assert m.runtime_minutes == 148
        assert m.genres == []
        assert m.rating is None
        assert m.certification is None
        assert m.year is None
        assert m.poster_url is None

    def test_creation_with_all_fields(self):
        m = Movie(
            title="Inception",
            runtime_minutes=148,
            genres=["Action", "Sci-Fi"],
            rating=8.8,
            certification="PG-13",
            year=2010,
        )
        assert m.title == "Inception"
        assert m.runtime_minutes == 148
        assert m.genres == ["Action", "Sci-Fi"]
        assert m.rating == pytest.approx(8.8)
        assert m.certification == "PG-13"
        assert m.year == 2010

    def test_equality(self):
        m1 = Movie(
            title="Inception",
            runtime_minutes=148,
            genres=["Action"],
            rating=8.8,
            certification="PG-13",
            year=2010,
        )
        m2 = Movie(
            title="Inception",
            runtime_minutes=148,
            genres=["Action"],
            rating=8.8,
            certification="PG-13",
            year=2010,
        )
        assert m1 == m2

    def test_inequality_different_certification(self):
        m1 = Movie(title="Movie", runtime_minutes=148, certification="R")
        m2 = Movie(title="Movie", runtime_minutes=148, certification="PG-13")
        assert m1 != m2

    def test_inequality_different_title(self):
        m1 = Movie(title="Inception", runtime_minutes=148)
        m2 = Movie(title="Interstellar", runtime_minutes=148)
        assert m1 != m2

    def test_inequality_different_runtime(self):
        m1 = Movie(title="Inception", runtime_minutes=148)
        m2 = Movie(title="Inception", runtime_minutes=149)
        assert m1 != m2

    def test_inequality_different_genres(self):
        m1 = Movie(title="Inception", runtime_minutes=148, genres=["Action"])
        m2 = Movie(title="Inception", runtime_minutes=148, genres=["Drama"])
        assert m1 != m2

    def test_inequality_different_rating(self):
        m1 = Movie(title="Inception", runtime_minutes=148, rating=8.8)
        m2 = Movie(title="Inception", runtime_minutes=148, rating=7.5)
        assert m1 != m2

    def test_lt_by_runtime(self):
        shorter = Movie(title="Inception", runtime_minutes=148)
        longer = Movie(title="Amadeus", runtime_minutes=180)
        assert shorter < longer

    def test_lt_by_title_when_same_runtime(self):
        a = Movie(title="Alpha", runtime_minutes=148)
        b = Movie(title="Beta", runtime_minutes=148)
        assert a < b

    def test_lt_case_insensitive(self):
        lower = Movie(title="alpha", runtime_minutes=148)
        upper = Movie(title="Beta", runtime_minutes=148)
        assert lower < upper

    def test_sort_movies(self):
        movies = [
            Movie(title="Zulu", runtime_minutes=200),
            Movie(title="Alpha", runtime_minutes=148),
            Movie(title="Beta", runtime_minutes=148),
            Movie(title="Middle", runtime_minutes=160),
        ]
        result = sorted(movies)
        assert result[0] == Movie(title="Alpha", runtime_minutes=148)
        assert result[1] == Movie(title="Beta", runtime_minutes=148)
        assert result[2] == Movie(title="Middle", runtime_minutes=160)
        assert result[3] == Movie(title="Zulu", runtime_minutes=200)

    def test_equality_not_implemented_for_non_movie(self):
        m = Movie(title="Inception", runtime_minutes=148)
        assert m.__eq__("not a movie") == NotImplemented

    def test_lt_not_implemented_for_non_movie(self):
        m = Movie(title="Inception", runtime_minutes=148)
        assert m.__lt__("not a movie") == NotImplemented

    def test_inequality_different_year(self):
        m1 = Movie(title="Inception", runtime_minutes=148, year=2010)
        m2 = Movie(title="Inception", runtime_minutes=148, year=2011)
        assert m1 != m2

    def test_creation_with_description(self):
        m = Movie(
            title="Inception",
            runtime_minutes=148,
            description="A thief who steals corporate secrets through the use of dream-sharing technology.",
        )
        assert m.title == "Inception"
        assert m.runtime_minutes == 148
        assert (
            m.description
            == "A thief who steals corporate secrets through the use of dream-sharing technology."
        )

    def test_default_description_is_none(self):
        m = Movie(title="Test", runtime_minutes=100)
        assert m.description is None

    def test_inequality_different_description(self):
        m1 = Movie(title="Inception", runtime_minutes=148, description="Description 1")
        m2 = Movie(title="Inception", runtime_minutes=148, description="Description 2")
        assert m1 != m2

    def test_creation_with_poster_url(self):
        m = Movie(
            title="Inception",
            runtime_minutes=148,
            poster_url="https://image.tmdb.org/t/p/w500/abc123.jpg",
        )
        assert m.title == "Inception"
        assert m.runtime_minutes == 148
        assert m.poster_url == "https://image.tmdb.org/t/p/w500/abc123.jpg"

    def test_default_poster_url_is_none(self):
        m = Movie(title="Test", runtime_minutes=100)
        assert m.poster_url is None

    def test_inequality_different_poster_url(self):
        m1 = Movie(title="Inception", runtime_minutes=148, poster_url="url1.jpg")
        m2 = Movie(title="Inception", runtime_minutes=148, poster_url="url2.jpg")
        assert m1 != m2
