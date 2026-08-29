"""UI regression tests for the runtime filter / display-mode toggle.

These tests exist to prevent a regression where `.filter-group { display: flex }`
in site/styles.css had equal CSS specificity to the browser's default
`[hidden] { display: none }` rule. Because the author stylesheet wins over the
user-agent stylesheet at equal specificity, the `display: flex` rule silently
overrode the `hidden` attribute that app.js was setting, so both the
minutes-only and hours+minutes filter input groups rendered simultaneously
regardless of the "Show Runtime in Minutes" / "Show Runtime in Hrs & Mins"
toggle state. The fix adds a more-specific `.filter-group[hidden]` CSS
rule that overrides the `display: flex` rule for the inactive group.
"""

from __future__ import annotations

from playwright.sync_api import expect


def test_default_mode_shows_only_hours_minutes_inputs(site_page):
    """By default (hours_minutes mode) only the hour+minute filter inputs show."""
    page = site_page

    expect(page.locator("#min-runtime-hm-group")).to_be_visible()
    expect(page.locator("#max-runtime-hm-group")).to_be_visible()
    expect(page.locator("#min-runtime-group")).to_be_hidden()
    expect(page.locator("#max-runtime-group")).to_be_hidden()


def test_toggle_switches_to_minutes_only_inputs(site_page):
    """Clicking the display toggle switches the filter inputs to minutes-only."""
    page = site_page

    page.click("#runtime-format-toggle")

    expect(page.locator("#min-runtime-group")).to_be_visible()
    expect(page.locator("#max-runtime-group")).to_be_visible()
    expect(page.locator("#min-runtime-hm-group")).to_be_hidden()
    expect(page.locator("#max-runtime-hm-group")).to_be_hidden()


def test_toggle_back_restores_hours_minutes_inputs(site_page):
    """Toggling twice returns to the original hours+minutes filter inputs."""
    page = site_page

    page.click("#runtime-format-toggle")
    page.click("#runtime-format-toggle")

    expect(page.locator("#min-runtime-hm-group")).to_be_visible()
    expect(page.locator("#max-runtime-hm-group")).to_be_visible()
    expect(page.locator("#min-runtime-group")).to_be_hidden()
    expect(page.locator("#max-runtime-group")).to_be_hidden()


def test_only_one_filter_input_format_visible_at_a_time(site_page):
    """Regression test: exactly one of the two filter input formats is ever visible.

    This directly guards against the CSS specificity bug described in the
    module docstring, by asserting the invariant across several toggles
    rather than only checking a single before/after snapshot.
    """
    page = site_page
    min_hm_group = page.locator("#min-runtime-hm-group")
    min_minutes_group = page.locator("#min-runtime-group")
    max_hm_group = page.locator("#max-runtime-hm-group")
    max_minutes_group = page.locator("#max-runtime-group")

    # Start in the known default state (hours+minutes visible) so each
    # iteration below can wait for a specific, deterministic state rather
    # than racing the click handler.
    expect(min_hm_group).to_be_visible()

    for _ in range(4):
        hm_visible = min_hm_group.is_visible()
        minutes_visible = min_minutes_group.is_visible()
        assert hm_visible != minutes_visible, (
            "Exactly one of the minute-only / hours+minutes filter groups "
            "should be visible at a time, never both or neither."
        )
        max_hm_visible = max_hm_group.is_visible()
        max_minutes_visible = max_minutes_group.is_visible()
        assert max_hm_visible != max_minutes_visible
        assert hm_visible == max_hm_visible

        page.click("#runtime-format-toggle")

        # Wait for the toggle to actually flip the visible group before the
        # next iteration reads state, so the assertions above never race
        # the click handler on slower CI runners.
        if hm_visible:
            expect(min_minutes_group).to_be_visible()
            expect(min_hm_group).to_be_hidden()
        else:
            expect(min_hm_group).to_be_visible()
            expect(min_minutes_group).to_be_hidden()


def test_default_values_convert_correctly_between_modes(site_page):
    """Switching modes preserves the equivalent runtime value (90m == 1h30m)."""
    page = site_page

    expect(page.locator("#min-runtime-hours")).to_have_value("1")
    expect(page.locator("#min-runtime-minutes")).to_have_value("30")
    expect(page.locator("#max-runtime-hours")).to_have_value("2")
    expect(page.locator("#max-runtime-minutes")).to_have_value("40")

    page.click("#runtime-format-toggle")

    expect(page.locator("#min-runtime")).to_have_value("90")
    expect(page.locator("#max-runtime")).to_have_value("160")


def test_apply_filters_rejects_min_greater_than_max(site_page):
    """Applying filters where min > max shows an inline validation error."""
    page = site_page

    page.fill("#min-runtime-hours", "5")
    page.fill("#min-runtime-minutes", "0")
    page.fill("#max-runtime-hours", "1")
    page.fill("#max-runtime-minutes", "0")
    page.click("#apply-filters")

    expect(page.locator("#filter-error")).to_have_text(
        "Minimum runtime cannot be greater than maximum runtime."
    )


def test_reset_filters_restores_defaults(site_page):
    """Reset restores the default runtime filter values in the active mode."""
    page = site_page

    page.click("#runtime-format-toggle")  # switch to minutes-only mode
    page.fill("#min-runtime", "50")
    page.fill("#max-runtime", "500")
    page.click("#reset-filters")

    expect(page.locator("#min-runtime")).to_have_value("90")
    expect(page.locator("#max-runtime")).to_have_value("160")


def test_movies_render_from_mocked_data(site_page):
    """Sanity check that the page renders movies from the (mocked) data feed."""
    page = site_page

    expect(page.locator("#movies-tbody")).to_contain_text("Alpha Film")
    expect(page.locator("#movies-tbody")).to_contain_text("Zulu Film")
