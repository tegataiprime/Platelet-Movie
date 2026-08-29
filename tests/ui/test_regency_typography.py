"""Regression tests for the Regency-inspired heading typography."""

from __future__ import annotations

from playwright.sync_api import expect


def test_page_and_section_titles_use_cormorant_garamond(site_page):
    """Page and section titles use the Regency-inspired display face."""
    expect(site_page.locator("h1")).to_have_css(
        "font-family",
        '"Cormorant Garamond", "Playfair Display", Georgia, serif',
    )
    expect(site_page.locator("section h2").first).to_have_css(
        "font-family",
        '"Cormorant Garamond", "Playfair Display", Georgia, serif',
    )
