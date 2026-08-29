"""Regression tests for decorative section-heading ornaments."""

from __future__ import annotations


def assert_balanced_heading_ornaments(heading, expected_text):
    """Assert a heading has mirrored, evenly spaced decorative ornaments."""
    assert heading.inner_text() == expected_text

    leading = heading.evaluate(
        "(element) => getComputedStyle(element, '::before').content"
    )
    transform = heading.evaluate(
        "(element) => getComputedStyle(element, '::before').transform"
    )
    margin_right = heading.evaluate(
        "(element) => getComputedStyle(element, '::before').marginRight"
    )
    margin_left = heading.evaluate(
        "(element) => getComputedStyle(element, '::after').marginLeft"
    )
    assert "❧" in leading
    assert transform.startswith("matrix(-1")
    assert margin_right == "6.4px"
    assert margin_left == margin_right


def test_filter_heading_uses_mirrored_leading_ornament(site_page):
    """Filter Movies uses matching ornaments instead of the target emoji."""
    assert_balanced_heading_ornaments(
        site_page.locator(".filters-section h2"),
        "Filter Movies",
    )


def test_movie_list_heading_uses_mirrored_leading_ornament(site_page):
    """Movie List uses the same balanced ornament treatment."""
    assert_balanced_heading_ornaments(
        site_page.locator(".movies-section h2"),
        "Movie List",
    )


def test_acknowledgements_heading_uses_mirrored_leading_ornament(site_page):
    """Acknowledgements uses the same balanced ornament treatment."""
    assert_balanced_heading_ornaments(
        site_page.locator(".acknowledgements-section h2"),
        "Acknowledgements & Disclaimers",
    )
