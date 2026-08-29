"""Behavior tests for the browser telemetry client."""

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
TELEMETRY_SCRIPT = PROJECT_ROOT / "site" / "telemetry.js"


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


def test_flush_waits_until_umami_track_is_available():
    """A script load without a usable tracker does not throw or discard events."""
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
loadHandler();
""",
    )

    assert len(tracked) == 1
