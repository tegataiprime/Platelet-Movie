"""Regression tests for the Regency-inspired heading typography."""

from __future__ import annotations

from playwright.sync_api import expect


def test_page_and_section_titles_use_ac_society(site_page):
    """Page and section titles prefer AC Society with safe fallbacks."""
    expect(site_page.locator("h1")).to_have_css(
        "font-family",
        '"AC Society", Baskerville, "Libre Baskerville", Georgia, serif',
    )
    expect(site_page.locator("section h2").first).to_have_css(
        "font-family",
        '"AC Society", Baskerville, "Libre Baskerville", Georgia, serif',
    )
    expect(site_page.locator(".acknowledgement-item h3").first).to_have_css(
        "font-family",
        '"AC Society", Baskerville, "Libre Baskerville", Georgia, serif',
    )
