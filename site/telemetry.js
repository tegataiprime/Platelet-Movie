const telemetry = (() => {
    const config = window.TELEMETRY_CONFIG;
    const eventQueue = [];
    const maxQueueSize = 100;
    const validSortFields = new Set([
        "title",
        "runtime_minutes",
        "year",
        "vote_average",
        "certification",
        "genres",
    ]);
    const validThemes = new Set(["light", "theater"]);
    const validRegions = new Set(["us", "gb", "in"]);
    const validRuntimeFormats = new Set(["hours_minutes", "minutes"]);
    const validFavoritesFilterModes = new Set(["all", "favorites"]);
    const validDescriptionStates = new Set(["expanded", "collapsed"]);
    const validOutboundDestinations = new Set(["tmdb", "red_cross", "github"]);

    function runtimeBucket(runtime) {
        if (runtime < 90) return "under-90";
        if (runtime < 120) return "90-119";
        if (runtime < 135) return "120-134";
        if (runtime < 160) return "135-159";
        return "160-plus";
    }

    function isConfigured() {
        return config?.enabled && config.websiteId && config.scriptUrl?.startsWith("https://");
    }

    function send(eventName, properties) {
        if (!isConfigured()) return;
        if (typeof window.umami?.track === "function") {
            flushQueue();
            window.umami.track(eventName, properties);
        } else {
            if (eventQueue.length >= maxQueueSize) eventQueue.shift();
            eventQueue.push([eventName, properties]);
        }
    }

    function flushQueue() {
        if (typeof window.umami?.track !== "function") return;
        while (eventQueue.length > 0) {
            const [eventName, properties] = eventQueue.shift();
            window.umami.track(eventName, properties);
        }
    }

    function loadUmami() {
        if (!config?.enabled) return;
        if (!isConfigured()) {
            console.warn("Telemetry is enabled but its Umami configuration is invalid.");
            return;
        }

        const script = document.createElement("script");
        script.src = config.scriptUrl;
        script.dataset.websiteId = config.websiteId;
        script.addEventListener("load", flushQueue);
        document.head.append(script);
    }

    loadUmami();

    return {
        trackDurationFilterChange(minimum, maximum) {
            if (
                typeof minimum !== "number"
                || typeof maximum !== "number"
                || !Number.isFinite(minimum)
                || (maximum !== Infinity && !Number.isFinite(maximum))
                || minimum < 0
                || maximum < 0
                || maximum < minimum
            ) {
                return;
            }
            send("filter_duration_changed", {
                minimum: runtimeBucket(minimum),
                maximum: runtimeBucket(maximum),
            });
        },
        trackSortChange(field, direction) {
            if (validSortFields.has(field) && ["asc", "desc"].includes(direction)) {
                send("sort_changed", { field, direction });
            }
        },
        trackFavoriteToggled(state) {
            if (["on", "off"].includes(state)) {
                send("favorite_toggled", { state });
            }
        },
        trackThemeChanged(theme) {
            if (validThemes.has(theme)) {
                send("theme_changed", { theme });
            }
        },
        trackRegionChanged(region) {
            if (validRegions.has(region)) {
                send("region_changed", { region });
            }
        },
        trackRuntimeDisplayChanged(format) {
            if (validRuntimeFormats.has(format)) {
                send("runtime_display_changed", { format });
            }
        },
        trackFiltersReset() {
            send("filters_reset", {});
        },
        trackFavoritesFilterChanged(mode) {
            if (validFavoritesFilterModes.has(mode)) {
                send("favorites_filter_changed", { mode });
            }
        },
        trackFavoritesCleared() {
            send("favorites_cleared", {});
        },
        trackDescriptionToggled(state) {
            if (validDescriptionStates.has(state)) {
                send("description_toggled", { state });
            }
        },
        trackOutboundLink(destination) {
            if (validOutboundDestinations.has(destination)) {
                send("outbound_link_clicked", { destination });
            }
        },
    };
})();
