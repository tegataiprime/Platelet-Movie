"""Regression tests for the Regency-inspired heading typography."""

from __future__ import annotations

from playwright.sync_api import expect


def test_page_and_section_titles_use_libre_baskerville(site_page):
    """Section and card titles use the open-source Libre Baskerville face."""
    expect(site_page.locator("section h2").first).to_have_css(
        "font-family",
        '"Libre Baskerville", Baskerville, Georgia, serif',
    )
    expect(site_page.locator("section h2").first).to_have_css(
        "font-optical-sizing",
        "auto",
    )


def test_site_title_is_available_to_assistive_technology_only(site_page):
    """The banner replaces the visible title without removing the page heading."""
    heading = site_page.locator("h1")

    expect(heading).to_have_text("Platelet-Movie")
    expect(heading).to_have_class("visually-hidden")
    expect(heading).to_have_css("position", "absolute")
    expect(heading).to_have_css("width", "1px")
    expect(heading).to_have_css("height", "1px")
    expect(site_page.locator(".acknowledgement-item h3").first).to_have_css(
        "font-family",
        '"Libre Baskerville", Baskerville, Georgia, serif',
    )
    expect(site_page.locator(".acknowledgement-item h3").first).to_have_css(
        "font-optical-sizing",
        "auto",
    )
