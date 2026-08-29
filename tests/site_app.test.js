const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

function loadApp(savedValues = {}) {
    const elements = Object.fromEntries(
        [
            'max-runtime',
            'max-runtime-hours',
            'max-runtime-minutes',
            'min-runtime',
            'min-runtime-hours',
            'min-runtime-minutes',
            'min-runtime-group',
            'max-runtime-group',
            'min-runtime-hm-group',
            'max-runtime-hm-group',
            'runtime-format-toggle',
        ].map(id => [id, { value: '', hidden: false, textContent: '' }])
    );
    const storage = new Map(Object.entries(savedValues));
    const context = vm.createContext({
        console,
        document: {
            documentElement: { dataset: { theme: 'light' } },
            addEventListener() {},
            getElementById(id) {
                return elements[id] || null;
            },
        },
        localStorage: {
            getItem(key) {
                return storage.has(key) ? storage.get(key) : null;
            },
            setItem(key, value) {
                storage.set(key, String(value));
            },
            removeItem(key) {
                storage.delete(key);
            },
        },
    });
    vm.runInContext(fs.readFileSync(path.resolve(__dirname, '../site/app.js'), 'utf8'), context);
    return { context, elements, storage };
}

test('setMaxRuntimeInputs clears every input for an unbounded maximum', () => {
    const { context, elements } = loadApp();
    elements['max-runtime'].value = '160';
    elements['max-runtime-hours'].value = '2';
    elements['max-runtime-minutes'].value = '40';

    vm.runInContext('setMaxRuntimeInputs(Infinity)', context);

    assert.equal(elements['max-runtime'].value, '');
    assert.equal(elements['max-runtime-hours'].value, '');
    assert.equal(elements['max-runtime-minutes'].value, '');
});

test('toggling runtime display preserves an unbounded maximum', () => {
    const { context, elements } = loadApp();
    elements['min-runtime'].value = '90';
    elements['max-runtime'].value = '';
    elements['max-runtime-hours'].value = '2';
    elements['max-runtime-minutes'].value = '40';
    vm.runInContext("runtimeDisplayMode = 'minutes'; renderMovies = () => {}", context);

    vm.runInContext('toggleRuntimeDisplayMode()', context);

    assert.equal(elements['max-runtime-hours'].value, '');
    assert.equal(elements['max-runtime-minutes'].value, '');
});

test('unbounded maximum runtime persists and reloads as empty inputs', () => {
    const { context, elements, storage } = loadApp({ maxRuntime: 'Infinity' });

    vm.runInContext('initFilters()', context);
    assert.equal(elements['max-runtime'].value, '');
    assert.equal(elements['max-runtime-hours'].value, '');
    assert.equal(elements['max-runtime-minutes'].value, '');

    vm.runInContext('saveFilterValues(90, Infinity)', context);
    assert.equal(storage.get('maxRuntime'), '');
});

test('applyRuntimeFilters only tracks duration changes when explicitly requested', () => {
    const { context, elements } = loadApp();
    elements['min-runtime'].value = '90';
    elements['max-runtime'].value = '160';

    vm.runInContext(
        `
runtimeDisplayMode = 'minutes';
allMovies = [{ tmdb_id: 1, runtime_minutes: 120 }];
filteredMovies = [...allMovies];
sortMovies = () => {};
renderMovies = () => {};
updateFilterResults = () => {};
telemetry = { trackDurationFilterChange: (...args) => globalThis.__tracked.push(args) };
globalThis.__tracked = [];
`,
        context
    );

    vm.runInContext('applyRuntimeFilters()', context);
    assert.equal(JSON.stringify(context.__tracked), JSON.stringify([]));

    vm.runInContext('applyRuntimeFilters(true)', context);
    assert.equal(JSON.stringify(context.__tracked), JSON.stringify([[90, 160]]));
});

test('trackTelemetry is a no-op when telemetry is unavailable', () => {
    const { context } = loadApp();
    assert.doesNotThrow(() =>
        vm.runInContext("trackTelemetry('trackSortChange', 'runtime_minutes', 'asc')", context)
    );
});

test('meaningful controls track their completed outcomes', () => {
    const { context, elements } = loadApp();
    elements['min-runtime'].value = '90';
    elements['max-runtime'].value = '160';

    vm.runInContext(
        `
globalThis.__tracked = [];
telemetry = new Proxy({}, {
    get: (_, method) => (...args) => globalThis.__tracked.push([method, ...args]),
});
updateThemeIcon = () => {};
updateFavouritesButtonText = () => {};
loadData = () => {};
renderMovies = () => {};
sortMovies = () => {};
updateFilterResults = () => {};
updateSortIndicators = () => {};
clearSavedFilters = () => {};
setMinRuntimeInputs = () => {};
setMaxRuntimeInputs = () => {};
allMovies = [];
filteredMovies = [];
`,
        context
    );

    vm.runInContext(`
        toggleTheme();
        changeRegion("gb");
        runtimeDisplayMode = "hours_minutes";
        toggleRuntimeDisplayMode();
        resetFilters();
        clearAllFavourites();
        handleSort("title");
    `, context);

    assert.deepEqual(JSON.parse(JSON.stringify(context.__tracked)), [
        ['trackThemeChanged', 'theater'],
        ['trackRegionChanged', 'gb'],
        ['trackRuntimeDisplayChanged', 'minutes'],
        ['trackFiltersReset'],
        ['trackFavoritesCleared'],
        ['trackSortChange', 'title', 'asc'],
    ]);
});

test('invalid actions and passive filter applications are not tracked', () => {
    const { context, elements } = loadApp();
    elements['min-runtime'].value = '200';
    elements['max-runtime'].value = '100';

    vm.runInContext(
        `
globalThis.__tracked = [];
telemetry = new Proxy({}, {
    get: (_, method) => (...args) => globalThis.__tracked.push([method, ...args]),
});
allMovies = [];
changeRegion("invalid");
runtimeDisplayMode = "minutes";
applyRuntimeFilters(true);
`,
        context
    );

    assert.deepEqual(JSON.parse(JSON.stringify(context.__tracked)), []);
});

test('favourites filter, description toggles, and categorized links are tracked', () => {
    const { context } = loadApp();

    vm.runInContext(
        `
globalThis.__tracked = [];
telemetry = new Proxy({}, {
    get: (_, method) => (...args) => globalThis.__tracked.push([method, ...args]),
});
const toggleButton = {
    dataset: { filterMode: "all" },
    querySelector: () => ({ textContent: "" }),
};
document.getElementById = id => id === "toggle-favourites" ? toggleButton : null;
applyRuntimeFilters = () => {};
handleToggleFavouritesFilter();

const row = {
    classList: { toggle: () => true },
    setAttribute() {},
};
toggleExpandableRow(row);

handleOutboundLinkClick({
    target: {
        closest: () => ({ dataset: { telemetryDestination: "red_cross" } }),
    },
});
`,
        context
    );

    assert.deepEqual(JSON.parse(JSON.stringify(context.__tracked)), [
        ['trackFavoritesFilterChanged', 'favorites'],
        ['trackDescriptionToggled', 'expanded'],
        ['trackOutboundLink', 'red_cross'],
    ]);
});
