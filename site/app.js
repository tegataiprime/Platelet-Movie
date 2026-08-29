// App.js - Main JavaScript for Platelet-Movie GitHub Pages Site

// State
let allMovies = [];
let filteredMovies = [];
let sortColumn = 'runtime_minutes';
let sortDirection = 'asc';
let currentRegion = 'us'; // Default region
let hasSavedFilters = false;
let expandableRowsController = null; // AbortController for event listeners
let favouritesFilterMode = 'all'; // 'all' or 'favourites'
let runtimeDisplayMode = 'hours_minutes'; // 'hours_minutes' or 'minutes'

// Constants
const BRITISH_REGIONS = new Set(['gb', 'in']);

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initRegion();
    initRuntimeDisplayMode();
    hasSavedFilters = initFilters();
    updateFavouritesButtonText(); // Set initial button text
    loadData();
    setupEventListeners();
});

// Region Management
function initRegion() {
    // Get saved region from localStorage or use default
    const savedRegion = localStorage.getItem('region') || 'us';
    currentRegion = savedRegion;
    
    // Set the select element to the saved region
    const regionSelect = document.getElementById('region-select');
    if (regionSelect) {
        regionSelect.value = savedRegion;
    }
}

function changeRegion(region) {
    // Validate region
    const validRegions = ['us', 'gb', 'in'];
    if (!validRegions.includes(region)) {
        console.error('Invalid region:', region);
        return;
    }
    
    // Save to localStorage
    localStorage.setItem('region', region);
    currentRegion = region;
    
    // Update favourites button text based on new region
    updateFavouritesButtonText();
    
    // Reload data for new region
    loadData();
}

function updateFavouritesButtonText() {
    const toggleBtn = document.getElementById('toggle-favourites');
    if (!toggleBtn) return;
    
    const buttonText = getButtonTextForRegion(favouritesFilterMode === 'favourites');
    const textElement = toggleBtn.querySelector('.favourites-toggle-text');
    if (textElement) {
        textElement.textContent = buttonText;
    }
    
    // Also update clear favourites button text
    const clearBtn = document.getElementById('clear-favourites');
    if (clearBtn) {
        const clearText = getClearFavouritesButtonText();
        const clearTextElement = clearBtn.querySelector('.clear-favourites-text');
        if (clearTextElement) {
            clearTextElement.textContent = clearText;
        }
    }
}

// Theme Management
function initTheme() {
    let savedTheme = localStorage.getItem('theme') || 'light';
    // Migrate legacy 'dark' value to new 'theater' theme name
    if (savedTheme === 'dark') {
        savedTheme = 'theater';
        localStorage.setItem('theme', savedTheme);
    }
    document.documentElement.dataset.theme = savedTheme;
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.dataset.theme;
    const newTheme = currentTheme === 'light' ? 'theater' : 'light';
    document.documentElement.dataset.theme = newTheme;
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('.theme-icon');
    if (icon) {
        icon.textContent = theme === 'light' ? '🌙' : '☀️';
    }
}

// Runtime Display Mode Management
function initRuntimeDisplayMode() {
    const saved = localStorage.getItem('runtimeDisplayMode');
    runtimeDisplayMode = saved === 'minutes' ? 'minutes' : 'hours_minutes';
    updateRuntimeToggleButton();
    updateFilterInputsVisibility();
}

function toggleRuntimeDisplayMode() {
    // Capture the currently entered filter values (as canonical minutes) before
    // switching modes so the new input representation shows equivalent values.
    const minMinutes = getMinRuntimeMinutes();
    const maxMinutesRaw = getMaxRuntimeMinutes();

    runtimeDisplayMode = runtimeDisplayMode === 'hours_minutes' ? 'minutes' : 'hours_minutes';
    localStorage.setItem('runtimeDisplayMode', runtimeDisplayMode);
    updateRuntimeToggleButton();
    updateFilterInputsVisibility();

    setMinRuntimeInputs(minMinutes);
    setMaxRuntimeInputs(maxMinutesRaw);

    renderMovies();
}

/**
 * Show/hide the minute-only vs hours+minutes filter input groups based on
 * the current runtime display mode.
 */
function updateFilterInputsVisibility() {
    const showHM = runtimeDisplayMode === 'hours_minutes';
    const minMinutesGroup = document.getElementById('min-runtime-group');
    const maxMinutesGroup = document.getElementById('max-runtime-group');
    const minHMGroup = document.getElementById('min-runtime-hm-group');
    const maxHMGroup = document.getElementById('max-runtime-hm-group');

    if (minMinutesGroup) minMinutesGroup.hidden = showHM;
    if (maxMinutesGroup) maxMinutesGroup.hidden = showHM;
    if (minHMGroup) minHMGroup.hidden = !showHM;
    if (maxHMGroup) maxHMGroup.hidden = !showHM;
}

/**
 * Convert a total number of minutes into an { hours, minutes } pair.
 * @param {number} totalMinutes - Runtime in minutes
 * @returns {{hours: number, minutes: number}}
 */
function minutesToHoursAndMinutes(totalMinutes) {
    const safeMinutes = Number.isFinite(totalMinutes) ? Math.max(0, totalMinutes) : 0;
    return {
        hours: Math.floor(safeMinutes / 60),
        minutes: safeMinutes % 60,
    };
}

/**
 * Convert separate hours and minutes values into a total minutes value.
 * @param {number|string} hours
 * @param {number|string} minutes
 * @returns {number}
 */
function hoursAndMinutesToMinutes(hours, minutes) {
    const h = Number.parseInt(hours, 10) || 0;
    const m = Number.parseInt(minutes, 10) || 0;
    return h * 60 + m;
}

/**
 * Write a canonical minutes value into the minimum runtime filter inputs
 * (both the minutes-only input and the hours+minutes inputs).
 * @param {number} totalMinutes
 */
function setMinRuntimeInputs(totalMinutes) {
    const minutesInput = document.getElementById('min-runtime');
    if (minutesInput) minutesInput.value = totalMinutes;

    const { hours, minutes } = minutesToHoursAndMinutes(totalMinutes);
    const hoursInput = document.getElementById('min-runtime-hours');
    const minutesInputHM = document.getElementById('min-runtime-minutes');
    if (hoursInput) hoursInput.value = hours;
    if (minutesInputHM) minutesInputHM.value = minutes;
}

/**
 * Write a canonical minutes value into the maximum runtime filter inputs
 * (both the minutes-only input and the hours+minutes inputs).
 * @param {number} totalMinutes
 */
function setMaxRuntimeInputs(totalMinutes) {
    const minutesInput = document.getElementById('max-runtime');
    const hoursInput = document.getElementById('max-runtime-hours');
    const minutesInputHM = document.getElementById('max-runtime-minutes');

    if (!Number.isFinite(totalMinutes)) {
        if (minutesInput) minutesInput.value = '';
        if (hoursInput) hoursInput.value = '';
        if (minutesInputHM) minutesInputHM.value = '';
        return;
    }

    if (minutesInput) minutesInput.value = totalMinutes;

    const { hours, minutes } = minutesToHoursAndMinutes(totalMinutes);
    if (hoursInput) hoursInput.value = hours;
    if (minutesInputHM) minutesInputHM.value = minutes;
}

/**
 * Read the current minimum runtime filter value (in minutes), from whichever
 * input representation is currently active.
 * @returns {number}
 */
function getMinRuntimeMinutes() {
    if (runtimeDisplayMode === 'minutes') {
        const input = document.getElementById('min-runtime');
        return Number.parseInt(input && input.value, 10) || 0;
    }
    const hoursInput = document.getElementById('min-runtime-hours');
    const minutesInput = document.getElementById('min-runtime-minutes');
    return hoursAndMinutesToMinutes(
        hoursInput && hoursInput.value,
        minutesInput && minutesInput.value
    );
}

/**
 * Read the current maximum runtime filter value (in minutes), from whichever
 * input representation is currently active. Returns Infinity when the field(s)
 * are empty, matching the "no upper bound" behaviour.
 * @returns {number}
 */
function getMaxRuntimeMinutes() {
    if (runtimeDisplayMode === 'minutes') {
        const input = document.getElementById('max-runtime');
        const value = input && input.value;
        if (value === '' || value === null || value === undefined) return Infinity;
        const parsed = Number.parseInt(value, 10);
        return Number.isNaN(parsed) ? Infinity : parsed;
    }
    const hoursInput = document.getElementById('max-runtime-hours');
    const minutesInput = document.getElementById('max-runtime-minutes');
    const hoursVal = hoursInput && hoursInput.value;
    const minutesVal = minutesInput && minutesInput.value;
    const bothEmpty =
        (hoursVal === '' || hoursVal === null || hoursVal === undefined) &&
        (minutesVal === '' || minutesVal === null || minutesVal === undefined);
    if (bothEmpty) return Infinity;
    return hoursAndMinutesToMinutes(hoursVal, minutesVal);
}

function updateRuntimeToggleButton() {
    const btn = document.getElementById('runtime-format-toggle');
    if (!btn) return;
    if (runtimeDisplayMode === 'hours_minutes') {
        btn.textContent = 'Show Runtime in Minutes';
    } else {
        btn.textContent = 'Show Runtime in Hrs & Mins';
    }
}

/**
 * Format a runtime value for display.
 * @param {number} minutes - Runtime in minutes
 * @returns {string} Formatted runtime string
 */
function formatRuntime(minutes) {
    if (!minutes && minutes !== 0) return '?';
    if (runtimeDisplayMode === 'minutes') {
        return `${minutes} m`;
    }
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    if (h === 0) return `${m} m`;
    if (m === 0) return `${h} h`;
    return `${h} h ${m} m`;
}

// Filter Persistence Management
function initFilters() {
    // Saved filter values are stored as canonical minutes regardless of display mode;
    // an empty maxRuntime value is the sentinel for an unbounded maximum.
    const savedMinRuntime = localStorage.getItem('minRuntime');
    const savedMaxRuntime = localStorage.getItem('maxRuntime');
    
    if (savedMinRuntime !== null) {
        setMinRuntimeInputs(Number.parseInt(savedMinRuntime, 10) || 0);
    }
    
    if (savedMaxRuntime !== null) {
        const parsedMaxRuntime = Number.parseInt(savedMaxRuntime, 10);
        setMaxRuntimeInputs(Number.isNaN(parsedMaxRuntime) ? Infinity : parsedMaxRuntime);
    }
    
    // Return true if saved filters exist
    return savedMinRuntime !== null || savedMaxRuntime !== null;
}

function saveFilterValues(minRuntime, maxRuntime) {
    localStorage.setItem('minRuntime', minRuntime);
    localStorage.setItem('maxRuntime', Number.isFinite(maxRuntime) ? maxRuntime : '');
}

function clearSavedFilters() {
    localStorage.removeItem('minRuntime');
    localStorage.removeItem('maxRuntime');
}

// Favourites Management
function getFavourites() {
    const favourites = localStorage.getItem('favouriteMovies');
    if (!favourites) {
        return {};
    }

    try {
        return JSON.parse(favourites);
    } catch (error) {
        // Handle corrupted localStorage data
        console.error('Failed to parse favourites from localStorage:', error);
        localStorage.removeItem('favouriteMovies');
        return {};
    }
}

function isFavourite(tmdbId) {
    if (!tmdbId) return false;
    const favourites = getFavourites();
    return favourites[tmdbId] === true;
}

function toggleFavourite(tmdbId) {
    if (!tmdbId) return;
    const favourites = getFavourites();
    
    if (favourites[tmdbId]) {
        delete favourites[tmdbId];
    } else {
        favourites[tmdbId] = true;
    }
    
    localStorage.setItem('favouriteMovies', JSON.stringify(favourites));
}

function getButtonTextForRegion(showFavouritesOnly) {
    // British English for UK and India, American English for US
    const useBritish = BRITISH_REGIONS.has(currentRegion);
    
    if (showFavouritesOnly) {
        return useBritish ? 'Show All Films' : 'Show All Movies';
    } else {
        return useBritish ? 'Show Favourites Only' : 'Show Favorites Only';
    }
}

function getClearFavouritesButtonText() {
    // British English for UK and India, American English for US
    const useBritish = BRITISH_REGIONS.has(currentRegion);
    return useBritish ? 'Clear All Favourites' : 'Clear All Favorites';
}

function getFavouriteAriaLabel(isFav) {
    // British English for UK and India, American English for US
    const useBritish = BRITISH_REGIONS.has(currentRegion);
    if (isFav) {
        return useBritish ? 'Remove from favourites' : 'Remove from favorites';
    } else {
        return useBritish ? 'Add to favourites' : 'Add to favorites';
    }
}

function validateAndParseTmdbId(tmdbIdStr) {
    if (!tmdbIdStr) return null;
    
    const tmdbId = Number.parseInt(tmdbIdStr, 10);
    // Validate that parsing succeeded and tmdbId is positive
    if (Number.isNaN(tmdbId) || tmdbId <= 0) {
        return null;
    }
    
    return tmdbId;
}

function updateFavouriteIcon(icon, tmdbId) {
    // Update the icon without re-rendering entire table
    const isFav = isFavourite(tmdbId);
    // SVG icon stays the same, only class changes for color
    icon.className = `favourite-icon ${isFav ? 'is-favourite' : 'not-favourite'}`;
    
    // Localize aria-label based on region
    const ariaLabel = getFavouriteAriaLabel(isFav);
    icon.setAttribute('aria-label', ariaLabel);
}

function clearAllFavourites() {
    // Clear from localStorage
    localStorage.removeItem('favouriteMovies');
    
    // Switch to "show all" mode to display all movies
    favouritesFilterMode = 'all';
    const toggleBtn = document.getElementById('toggle-favourites');
    if (toggleBtn) {
        toggleBtn.dataset.filterMode = 'all';
        const buttonText = getButtonTextForRegion(false);
        const textElement = toggleBtn.querySelector('.favourites-toggle-text');
        if (textElement) {
            textElement.textContent = buttonText;
        }
    }
    
    // Re-render to update drip icons and apply current runtime filters
    applyRuntimeFilters();
}

function trackTelemetry(methodName, ...args) {
    if (typeof telemetry === 'undefined') return;
    const method = telemetry[methodName];
    if (typeof method === 'function') {
        method(...args);
    }
}

// Event Listeners Setup
function setupEventListeners() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }

    const regionSelect = document.getElementById('region-select');
    if (regionSelect) {
        regionSelect.addEventListener('change', (e) => {
            changeRegion(e.target.value);
        });
    }

    const applyFiltersBtn = document.getElementById('apply-filters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', () => applyRuntimeFilters(true));
    }

    const resetFiltersBtn = document.getElementById('reset-filters');
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', resetFilters);
    }

    const toggleFavouritesBtn = document.getElementById('toggle-favourites');
    if (toggleFavouritesBtn) {
        toggleFavouritesBtn.addEventListener('click', handleToggleFavouritesFilter);
    }

    const clearFavouritesBtn = document.getElementById('clear-favourites');
    if (clearFavouritesBtn) {
        clearFavouritesBtn.addEventListener('click', clearAllFavourites);
    }

    const runtimeFormatToggleBtn = document.getElementById('runtime-format-toggle');
    if (runtimeFormatToggleBtn) {
        runtimeFormatToggleBtn.addEventListener('click', toggleRuntimeDisplayMode);
    }

    // Add sorting listeners to table headers with keyboard support
    const sortableHeaders = document.querySelectorAll('th.sortable');
    sortableHeaders.forEach(header => {
        // Click handler
        header.addEventListener('click', () => {
            const column = header.dataset.sort;
            handleSort(column);
        });
        
        // Keyboard handler (Enter or Space)
        header.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const column = header.dataset.sort;
                handleSort(column);
            }
        });
    });
    
    // Add window resize listener to re-check truncation on browser resize
    // Debounced to avoid performance issues
    window.addEventListener('resize', debounce(() => {
        initializeExpandableRows();
    }, 250));
}

// Data Loading
async function loadData() {
    try {
        // Construct the data file name based on current region with cache-busting parameter
        const dataFile = `data-${currentRegion}.json?t=${Date.now()}`;
        const response = await fetch(dataFile);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Load commentary
        displayCommentary(data.commentary);
        displayGeneratedAt(data.generated_at);
        
        // Load movies
        allMovies = data.movies || [];
        filteredMovies = [...allMovies];
        
        // Apply saved filters or favourites filter if they exist
        if (hasSavedFilters || favouritesFilterMode === 'favourites') {
            applyRuntimeFilters();
        }
        
        // Apply initial sort and render
        sortMovies();
        renderMovies();
        updateFilterResults();
        updateSortIndicators(); // Initialize aria-sort attributes
    } catch (error) {
        console.error('Error loading data:', error);
        displayError('Failed to load movie data. Please try refreshing the page.');
    }
}

// Commentary Display
function displayCommentary(commentary) {
    const commentaryElement = document.getElementById('commentary');
    if (commentaryElement && commentary) {
        // Split by newlines and wrap each paragraph
        const paragraphs = commentary.split('\n\n')
            .filter(p => p.trim())
            .map(p => `<p>${escapeHtml(p.trim())}</p>`)
            .join('');
        commentaryElement.innerHTML = paragraphs;
    }
}

function displayGeneratedAt(timestamp) {
    const element = document.getElementById('generated-at');
    if (element && timestamp) {
        const date = new Date(timestamp);
        element.textContent = `Last updated: ${date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZoneName: 'short'
        })}`;
    }
}

function getColumnCount() {
    // Calculate colspan dynamically based on number of columns
    const headerCells = document.querySelectorAll('thead th');
    return headerCells.length || 7; // Fallback to 7 if not found
}

// Error Display
function displayError(message) {
    const commentaryElement = document.getElementById('commentary');
    if (commentaryElement) {
        commentaryElement.innerHTML = `<p class="error">${escapeHtml(message)}</p>`;
    }
    
    const tbody = document.getElementById('movies-tbody');
    if (tbody) {
        const colspan = getColumnCount();
        tbody.innerHTML = `<tr><td colspan="${colspan}" class="loading-row">${escapeHtml(message)}</td></tr>`;
    }
}

// Movie Rendering
function renderMovies() {
    const tbody = document.getElementById('movies-tbody');
    if (!tbody) return;

    if (filteredMovies.length === 0) {
        const colspan = getColumnCount();
        tbody.innerHTML = `<tr><td colspan="${colspan}" class="loading-row">No movies found matching the filter criteria.</td></tr>`;
        return;
    }

    const rows = filteredMovies.map((movie, index) => {
        const genres = Array.isArray(movie.genres) 
            ? movie.genres.join(', ') 
            : movie.genres || 'N/A';
        
        const description = movie.description || 'N/A';
        
        // Build poster HTML if available
        const posterHtml = movie.poster_url 
            ? `<img src="${escapeHtml(movie.poster_url)}" alt="${escapeHtml(movie.title || 'Unknown')} poster" class="movie-poster" loading="lazy">`
            : '';
        
        // Determine if this movie is a favourite
        const isFav = isFavourite(movie.tmdb_id);
        const dripClass = isFav ? 'is-favourite' : 'not-favourite';
        // Use SVG droplet icon instead of emoji for better color control
        const dripIcon = `<svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
            <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
        </svg>`;
        
        // Localize aria-label based on region
        const ariaLabel = getFavouriteAriaLabel(isFav);
        
        return `
            <tr data-movie-index="${index}">
                <td class="favourite-column">
                    <button 
                        class="favourite-icon ${dripClass}" 
                        data-tmdb-id="${movie.tmdb_id || ''}"
                        aria-label="${ariaLabel}"
                        tabindex="0"
                    >${dripIcon}</button>
                </td>
                <td>
                    <div class="movie-title-container">
                        ${posterHtml}
                        <div class="movie-info">
                            <div class="movie-title">${escapeHtml(movie.title || 'Unknown')}</div>
                            <div class="movie-description">${escapeHtml(description)}</div>
                        </div>
                    </div>
                </td>
                <td>${formatRuntime(movie.runtime_minutes)}</td>
                <td>${movie.year || 'N/A'}</td>
                <td>${movie.vote_average === null || movie.vote_average === undefined ? 'N/A' : movie.vote_average.toFixed(1)}</td>
                <td>${escapeHtml(movie.certification || 'N/A')}</td>
                <td>${escapeHtml(genres)}</td>
            </tr>
        `;
    }).join('');

    tbody.innerHTML = rows;
    
    // Wait for the browser to lay out the clamped descriptions before measuring
    // scrollHeight/clientHeight. Measuring synchronously after innerHTML is set can
    // report equal heights and leave truncated rows without expansion controls.
    requestAnimationFrame(() => {
        initializeExpandableRows();
    });

    // Web fonts can change line wrapping after the first layout pass.
    if ("fonts" in document) {
        document.fonts.ready.then(() => {
            initializeExpandableRows();
        });
    }
    
    // Add click handlers for favourite icons
    addFavouriteIconListeners();
}

// Filtering
function applyRuntimeFilters(trackDurationChange = false) {
    const minRuntime = getMinRuntimeMinutes();
    const maxRuntime = getMaxRuntimeMinutes();
    const errorElement = document.getElementById('filter-error');

    // Clear any previous error
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.classList.remove('show');
    }

    if (minRuntime > maxRuntime) {
        // Use inline error message instead of alert
        if (errorElement) {
            errorElement.textContent = 'Minimum runtime cannot be greater than maximum runtime.';
            errorElement.classList.add('show');
        }
        return;
    }

    // Save filter values to localStorage
    saveFilterValues(minRuntime, maxRuntime);

    filteredMovies = allMovies.filter(movie => {
        const runtime = movie.runtime_minutes || 0;
        const runtimeMatch = runtime >= minRuntime && runtime <= maxRuntime;
        
        // If in favourites mode, also filter by favourite status
        if (favouritesFilterMode === 'favourites') {
            return runtimeMatch && isFavourite(movie.tmdb_id);
        }
        
        return runtimeMatch;
    });

    sortMovies();
    renderMovies();
    updateFilterResults();
    if (trackDurationChange) {
        trackTelemetry('trackDurationFilterChange', minRuntime, maxRuntime);
    }
}

function resetFilters() {
    setMinRuntimeInputs(90);
    setMaxRuntimeInputs(160);
    
    // Clear saved filter values from localStorage
    clearSavedFilters();
    
    // Clear any error message
    const errorElement = document.getElementById('filter-error');
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.classList.remove('show');
    }
    
    // Reset favourites filter mode to "all"
    favouritesFilterMode = 'all';
    const toggleBtn = document.getElementById('toggle-favourites');
    if (toggleBtn) {
        toggleBtn.dataset.filterMode = 'all';
        const buttonText = getButtonTextForRegion(false); // false = not showing favourites only
        const textElement = toggleBtn.querySelector('.favourites-toggle-text');
        if (textElement) {
            textElement.textContent = buttonText;
        }
    }
    
    filteredMovies = [...allMovies];
    sortMovies();
    renderMovies();
    updateFilterResults();
}

function updateFilterResults() {
    const element = document.getElementById('filter-results');
    if (element) {
        element.textContent = `Showing ${filteredMovies.length} of ${allMovies.length} movies`;
    }
}

// Favourites Icon Listeners
function addFavouriteIconListeners() {
    const favouriteIcons = document.querySelectorAll('.favourite-icon');
    favouriteIcons.forEach(icon => {
        const handleClick = (e) => {
            e.stopPropagation(); // Prevent row expansion
            e.preventDefault(); // Prevent any default button behavior
            
            const tmdbId = validateAndParseTmdbId(icon.dataset.tmdbId);
            if (!tmdbId) return;
            
            toggleFavourite(tmdbId);
            updateFavouriteIcon(icon, tmdbId);
            
            // If in favourites-only mode and this was unfavourited, refresh the view
            const isFav = isFavourite(tmdbId);
            trackTelemetry('trackFavoriteToggled', isFav ? 'on' : 'off');
            if (favouritesFilterMode === 'favourites' && !isFav) {
                applyRuntimeFilters();
            }
        };
        
        icon.addEventListener('click', handleClick);
        
        // Add keyboard support
        const handleKeydown = (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                e.stopPropagation();
                icon.click(); // Trigger the click handler
            }
        };
        
        icon.addEventListener('keydown', handleKeydown);
    });
}

// Favourites Filter Toggle
function handleToggleFavouritesFilter() {
    const toggleBtn = document.getElementById('toggle-favourites');
    if (!toggleBtn) return;
    
    // Toggle the mode
    favouritesFilterMode = favouritesFilterMode === 'all' ? 'favourites' : 'all';
    
    // Update button text based on region
    const buttonText = getButtonTextForRegion(favouritesFilterMode === 'favourites');
    const textElement = toggleBtn.querySelector('.favourites-toggle-text');
    if (textElement) {
        textElement.textContent = buttonText;
    }
    
    // Update button state
    toggleBtn.dataset.filterMode = favouritesFilterMode;
    
    // Apply the filter
    applyRuntimeFilters();
}

// Sorting
function handleSort(column) {
    if (sortColumn === column) {
        // Toggle direction if same column
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        // New column, default to ascending
        sortColumn = column;
        sortDirection = 'asc';
    }

    sortMovies();
    renderMovies();
    updateSortIndicators();
    trackTelemetry('trackSortChange', sortColumn, sortDirection);
}

function sortMovies() {
    filteredMovies.sort((a, b) => {
        let aVal = a[sortColumn];
        let bVal = b[sortColumn];

        // Handle null/undefined values
        if (aVal === null || aVal === undefined) aVal = '';
        if (bVal === null || bVal === undefined) bVal = '';

        // Handle numeric columns
        if (['runtime_minutes', 'year', 'vote_average'].includes(sortColumn)) {
            aVal = Number.parseFloat(aVal) || 0;
            bVal = Number.parseFloat(bVal) || 0;
        } else if (sortColumn === 'genres') {
            // Handle genres array - convert to string for sorting
            aVal = Array.isArray(aVal) ? aVal.join(', ').toLowerCase() : String(aVal).toLowerCase();
            bVal = Array.isArray(bVal) ? bVal.join(', ').toLowerCase() : String(bVal).toLowerCase();
        } else {
            // Convert to string for text comparison
            aVal = String(aVal).toLowerCase();
            bVal = String(bVal).toLowerCase();
        }

        let comparison = 0;
        if (aVal < bVal) comparison = -1;
        if (aVal > bVal) comparison = 1;

        return sortDirection === 'asc' ? comparison : -comparison;
    });
}

function updateSortIndicators() {
    // Remove all sorting classes and reset aria-sort
    document.querySelectorAll('th.sortable').forEach(th => {
        th.classList.remove('sorted-asc', 'sorted-desc');
        th.setAttribute('aria-sort', 'none');
    });

    // Add class and aria-sort to current sorted column
    const currentHeader = document.querySelector(`th[data-sort="${sortColumn}"]`);
    if (currentHeader) {
        currentHeader.classList.add(`sorted-${sortDirection}`);
        currentHeader.setAttribute('aria-sort', sortDirection === 'asc' ? 'ascending' : 'descending');
    }
}

// Utility Functions
function escapeHtml(unsafe) {
    if (typeof unsafe !== 'string') return unsafe;
    return unsafe
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

/**
 * Initialize expandable rows with event delegation.
 * Detects truncated movie descriptions and adds click/keyboard handlers
 * to allow users to expand and collapse rows to view full descriptions.
 * Uses AbortController to manage event listener lifecycle.
 */
function initializeExpandableRows() {
    const tbody = document.getElementById('movies-tbody');
    if (!tbody) return;
    
    // Cancel previous event listeners if they exist
    if (expandableRowsController) {
        expandableRowsController.abort();
    }
    
    // Create new AbortController for this set of listeners
    expandableRowsController = new AbortController();
    const signal = expandableRowsController.signal;
    
    const movieRows = tbody.querySelectorAll('tr');
    
    movieRows.forEach(row => {
        const descriptionElement = row.querySelector('.movie-description');
        if (!descriptionElement) return;
        
        // Clear previous truncation state
        descriptionElement.classList.remove('truncated');
        row.classList.remove('expanded');
        row.removeAttribute('tabindex');
        row.removeAttribute('role');
        row.removeAttribute('aria-expanded');
        row.removeAttribute('aria-describedby');
        
        // Check if the description is truncated
        if (isTextTruncated(descriptionElement)) {
            descriptionElement.classList.add('truncated');
            
            // Add keyboard accessibility attributes
            row.setAttribute('tabindex', '0');
            row.setAttribute('role', 'button');
            row.setAttribute('aria-expanded', 'false');
            row.setAttribute('aria-describedby', 'expand-hint');
        }
    });
    
    // Use event delegation on tbody for all click and keyboard events
    tbody.addEventListener('click', (e) => {
        const row = e.target.closest('tr[role="button"]');
        if (!row) return;
        
        // Don't expand/collapse if clicking on a link or within a link
        if (e.target.closest('a')) return;
        
        const isExpanded = row.classList.toggle('expanded');
        row.setAttribute('aria-expanded', isExpanded);
    }, { signal });
    
    tbody.addEventListener('keydown', (e) => {
        const row = e.target.closest('tr[role="button"]');
        if (!row) return;
        
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            const isExpanded = row.classList.toggle('expanded');
            row.setAttribute('aria-expanded', isExpanded);
        }
    }, { signal });
}

/**
 * Check if a text element's content is visually truncated.
 * @param {HTMLElement} element - The DOM element to check for truncation
 * @returns {boolean} True if the element's content exceeds its visible height and is truncated
 */
function isTextTruncated(element) {
    // The element is truncated if its scrollHeight exceeds its clientHeight
    return element.scrollHeight > element.clientHeight;
}

/**
 * Debounce function to limit how often a function can be called.
 * @param {Function} func - The function to debounce
 * @param {number} wait - The number of milliseconds to wait
 * @returns {Function} The debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
