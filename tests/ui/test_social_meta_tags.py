"""UI tests verifying Open Graph, Twitter Card meta tags, and the header banner.

These tests assert that:
- The required OG and Twitter Card meta tags are present in the page <head>.
- The header banner image is rendered and visible.
"""

from __future__ import annotations

from playwright.sync_api import expect


# ---------------------------------------------------------------------------
# Open Graph meta tags
# ---------------------------------------------------------------------------

def test_og_type(site_page):
    """og:type must be 'website'."""
    value = site_page.get_attribute('meta[property="og:type"]', "content")
    assert value == "website"


def test_og_url(site_page):
    """og:url must be set."""
    value = site_page.get_attribute('meta[property="og:url"]', "content")
    assert value is not None
    assert len(value) > 0


def test_og_title(site_page):
    """og:title must be set."""
    value = site_page.get_attribute('meta[property="og:title"]', "content")
    assert value is not None
    assert len(value) > 0


def test_og_description(site_page):
    """og:description must be set."""
    value = site_page.get_attribute('meta[property="og:description"]', "content")
    assert value is not None
    assert len(value) > 0


def test_og_image(site_page):
    """og:image must point to preview.png."""
    value = site_page.get_attribute('meta[property="og:image"]', "content")
    assert value is not None
    assert "preview.png" in value


def test_og_image_dimensions(site_page):
    """og:image:width and og:image:height must both be set."""
    width = site_page.get_attribute('meta[property="og:image:width"]', "content")
    height = site_page.get_attribute('meta[property="og:image:height"]', "content")
    assert width == "1672"
    assert height == "941"


# ---------------------------------------------------------------------------
# Twitter Card meta tags
# ---------------------------------------------------------------------------

def test_twitter_card(site_page):
    """twitter:card must be 'summary_large_image'."""
    value = site_page.get_attribute('meta[name="twitter:card"]', "content")
    assert value == "summary_large_image"


def test_twitter_title(site_page):
    """twitter:title must be set."""
    value = site_page.get_attribute('meta[name="twitter:title"]', "content")
    assert value is not None
    assert len(value) > 0


def test_twitter_description(site_page):
    """twitter:description must be set."""
    value = site_page.get_attribute('meta[name="twitter:description"]', "content")
    assert value is not None
    assert len(value) > 0


def test_twitter_image(site_page):
    """twitter:image must point to preview.png."""
    value = site_page.get_attribute('meta[name="twitter:image"]', "content")
    assert value is not None
    assert "preview.png" in value


# ---------------------------------------------------------------------------
# Header banner image
# ---------------------------------------------------------------------------

def test_header_banner_image_is_visible(site_page):
    """The banner <img> inside .header-banner must be visible."""
    banner = site_page.locator(".header-banner-img")
    expect(banner).to_be_visible()


def test_header_banner_image_src(site_page):
    """The banner image src must reference preview.png."""
    src = site_page.get_attribute(".header-banner-img", "src")
    assert src is not None
    assert "preview.png" in src


def test_header_banner_image_has_alt(site_page):
    """The banner image must have a non-empty alt attribute."""
    alt = site_page.get_attribute(".header-banner-img", "alt")
    assert alt is not None
    assert len(alt) > 0
