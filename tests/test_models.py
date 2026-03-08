"""Unit tests for platelet_movie.models."""

from platelet_movie.models import Movie


class TestMovie:
    def test_creation(self):
        m = Movie(title="Inception", runtime_minutes=148)
        assert m.title == "Inception"
        assert m.runtime_minutes == 148

    def test_equality(self):
        m1 = Movie(title="Inception", runtime_minutes=148)
        m2 = Movie(title="Inception", runtime_minutes=148)
        assert m1 == m2

    def test_inequality_different_title(self):
        m1 = Movie(title="Inception", runtime_minutes=148)
        m2 = Movie(title="Interstellar", runtime_minutes=148)
        assert m1 != m2

    def test_inequality_different_runtime(self):
        m1 = Movie(title="Inception", runtime_minutes=148)
        m2 = Movie(title="Inception", runtime_minutes=149)
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
