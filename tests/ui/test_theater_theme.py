"""Regression tests for theater-theme contrast and expandable movie rows."""

from __future__ import annotations

import re

from playwright.sync_api import expect


def test_theater_theme_uses_dark_safe_commentary_colors(site_page):
    """Commentary text remains legible against its theater-theme background."""
    page = site_page

    page.click("#theme-toggle")

    commentary = page.locator(".commentary-content")
    expect(commentary).to_have_css("background-color", "rgb(44, 32, 56)")
    expect(commentary).to_have_css("color", "rgb(245, 236, 223)")


def test_truncated_description_row_expands_in_theater_theme(site_page):
    """A truncated description remains clickable and readable when expanded."""
    page = site_page
    page.click("#theme-toggle")

    row = page.locator('#movies-tbody tr[role="button"]').first
    expect(row).to_have_attribute("aria-expanded", "false")

    row.click()

    expect(row).to_have_class(re.compile(r"\bexpanded\b"))
    expect(row).to_have_attribute("aria-expanded", "true")
    expect(row).to_have_css("background-color", "rgb(44, 32, 56)")
    expect(row).to_have_css("color", "rgb(245, 236, 223)")
    expect(row.locator(".movie-description")).to_have_css("-webkit-line-clamp", "none")
