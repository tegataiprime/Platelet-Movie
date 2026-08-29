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
