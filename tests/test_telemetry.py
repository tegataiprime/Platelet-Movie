"""Behavior tests for the browser telemetry client."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")

PROJECT_ROOT = Path(__file__).parent.parent
TELEMETRY_SCRIPT = PROJECT_ROOT / "site" / "telemetry.js"
INDEX_HTML = PROJECT_ROOT / "site" / "index.html"


def run_telemetry(config, actions):
    """Execute telemetry.js with a minimal browser environment."""
    harness = f"""
const fs = require("fs");
const vm = require("vm");
const tracked = [];
let loadHandler;
const window = {{ TELEMETRY_CONFIG: {json.dumps(config)} }};
const context = {{
    window,
    console: {{ warn() {{}} }},
    document: {{
        createElement() {{
            return {{
                dataset: {{}},
                addEventListener(event, handler) {{
                    if (event === "load") loadHandler = handler;
                }},
            }};
        }},
        head: {{ append() {{}} }},
    }},
}};
vm.createContext(context);
vm.runInContext(fs.readFileSync({json.dumps(str(TELEMETRY_SCRIPT))}, "utf8"), context);
{actions}
console.log(JSON.stringify(tracked));
"""
    result = subprocess.run(
        ["node", "-e", harness],
        capture_output=True,
        check=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_unconfigured_telemetry_does_not_send_events():
    """Disabled or invalid telemetry ignores events even when Umami exists."""
    configs = [
        {"enabled": False},
        {"enabled": True, "websiteId": "", "scriptUrl": "https://example.com/script.js"},
    ]

    for config in configs:
        tracked = run_telemetry(
            config,
            """
window.umami = { track: (...args) => tracked.push(args) };
vm.runInContext('telemetry.trackFavoriteToggled("on")', context);
""",
        )

        assert tracked == []


def test_queue_is_bounded_while_tracker_is_unavailable():
    """A blocked tracker cannot cause unbounded event queue growth."""
    tracked = run_telemetry(
        {
            "enabled": True,
            "websiteId": "website-id",
            "scriptUrl": "https://example.com/script.js",
        },
        """
for (let index = 0; index < 101; index += 1) {
    vm.runInContext('telemetry.trackFavoriteToggled("on")', context);
}
window.umami = { track: (...args) => tracked.push(args) };
loadHandler();
""",
    )

    assert len(tracked) == 100


def test_send_flushes_queue_when_umami_track_becomes_available():
    """The next event flushes queued events after late tracker initialization."""
    tracked = run_telemetry(
        {
            "enabled": True,
            "websiteId": "website-id",
            "scriptUrl": "https://example.com/script.js",
        },
        """
vm.runInContext('telemetry.trackFavoriteToggled("on")', context);
window.umami = {};
loadHandler();
window.umami.track = (...args) => tracked.push(args);
vm.runInContext('telemetry.trackFavoriteToggled("off")', context);
""",
    )

    assert tracked == [
        ["favorite_toggled", {"state": "on"}],
        ["favorite_toggled", {"state": "off"}],
    ]


def test_meaningful_interactions_emit_privacy_safe_events():
    """Every public tracker emits only its stable, low-cardinality properties."""
    tracked = run_telemetry(
        {
            "enabled": True,
            "websiteId": "website-id",
            "scriptUrl": "https://example.com/script.js",
        },
        """
window.umami = { track: (...args) => tracked.push(args) };
vm.runInContext(`
    telemetry.trackDurationFilterChange(90, Infinity);
    telemetry.trackThemeChanged("theater");
    telemetry.trackRegionChanged("gb");
    telemetry.trackRuntimeDisplayChanged("minutes");
    telemetry.trackFiltersReset();
    telemetry.trackFavoritesFilterChanged("favorites");
    telemetry.trackFavoritesCleared();
    telemetry.trackDescriptionToggled("expanded");
    telemetry.trackOutboundLink("github");
`, context);
""",
    )

    assert tracked == [
        ["filter_duration_changed", {"minimum": "90-119", "maximum": "160-plus"}],
        ["theme_changed", {"theme": "theater"}],
        ["region_changed", {"region": "gb"}],
        ["runtime_display_changed", {"format": "minutes"}],
        ["filters_reset", {}],
        ["favorites_filter_changed", {"mode": "favorites"}],
        ["favorites_cleared", {}],
        ["description_toggled", {"state": "expanded"}],
        ["outbound_link_clicked", {"destination": "github"}],
    ]


def test_interaction_trackers_reject_arbitrary_property_values():
    """Tracker methods cannot forward freeform values to Umami."""
    tracked = run_telemetry(
        {
            "enabled": True,
            "websiteId": "website-id",
            "scriptUrl": "https://example.com/script.js",
        },
        """
window.umami = { track: (...args) => tracked.push(args) };
vm.runInContext(`
    telemetry.trackDurationFilterChange("raw input", 160);
    telemetry.trackDurationFilterChange(90, NaN);
    telemetry.trackSortChange("movie title", "asc");
    telemetry.trackFavoriteToggled("movie-123");
    telemetry.trackThemeChanged("custom-theme");
    telemetry.trackRegionChanged("precise-location");
    telemetry.trackRuntimeDisplayChanged("seconds");
    telemetry.trackFavoritesFilterChanged("custom");
    telemetry.trackDescriptionToggled("movie-title");
    telemetry.trackOutboundLink("https://example.com/private?q=value");
`, context);
""",
    )

    assert tracked == []


def test_root_loads_tracker_once_and_categorizes_outbound_links():
    """The root owns one tracker instance and links expose only allowlisted categories."""
    html = INDEX_HTML.read_text(encoding="utf-8")

    assert html.count('src="telemetry.js"') == 1
    for destination in ("tmdb", "red_cross", "github"):
        assert f'data-telemetry-destination="{destination}"' in html
