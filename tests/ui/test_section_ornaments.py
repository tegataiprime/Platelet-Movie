"""Regression tests for decorative section-heading ornaments."""

from __future__ import annotations


def test_filter_heading_uses_mirrored_leading_ornament(site_page):
    """Filter Movies uses matching ornaments instead of the target emoji."""
    heading = site_page.locator(".filters-section h2")

    assert heading.inner_text() == "Filter Movies"
    leading = heading.evaluate(
        "(element) => getComputedStyle(element, '::before').content"
    )
    transform = heading.evaluate(
        "(element) => getComputedStyle(element, '::before').transform"
    )
    assert "❧" in leading
    assert transform.startswith("matrix(-1")
