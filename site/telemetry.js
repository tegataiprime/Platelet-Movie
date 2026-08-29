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
    };
})();
