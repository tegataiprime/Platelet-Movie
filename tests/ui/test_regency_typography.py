"""Regression tests for the Regency-inspired heading typography."""

from __future__ import annotations

from playwright.sync_api import expect


def test_page_and_section_titles_use_libre_baskerville(site_page):
    """Page and section titles use the open-source Libre Baskerville face."""
    expect(site_page.locator("h1")).to_have_css(
        "font-family",
        '"Libre Baskerville", Baskerville, Georgia, serif',
    )
    expect(site_page.locator("section h2").first).to_have_css(
        "font-family",
        '"Libre Baskerville", Baskerville, Georgia, serif',
    )
    expect(site_page.locator(".acknowledgement-item h3").first).to_have_css(
        "font-family",
        '"Libre Baskerville", Baskerville, Georgia, serif',
    )
