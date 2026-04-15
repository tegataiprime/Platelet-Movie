// App.js - Main JavaScript for Platelet-Movie GitHub Pages Site

// State
let allMovies = [];
let filteredMovies = [];
let sortColumn = 'runtime_minutes';
let sortDirection = 'asc';

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    loadData();
    setupEventListeners();
});

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.dataset.theme;
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('.theme-icon');
    if (icon) {
        icon.textContent = theme === 'light' ? '🌙' : '☀️';
    }
}

// Event Listeners Setup
function setupEventListeners() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }

    const applyFiltersBtn = document.getElementById('apply-filters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyRuntimeFilters);
    }

    const resetFiltersBtn = document.getElementById('reset-filters');
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', resetFilters);
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
}

// Data Loading
async function loadData() {
    try {
        const response = await fetch('data.json');
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

// Error Display
function displayError(message) {
    const commentaryElement = document.getElementById('commentary');
    if (commentaryElement) {
        commentaryElement.innerHTML = `<p class="error">${escapeHtml(message)}</p>`;
    }
    
    const tbody = document.getElementById('movies-tbody');
    if (tbody) {
        tbody.innerHTML = `<tr><td colspan="6" class="loading-row">${escapeHtml(message)}</td></tr>`;
    }
}

// Movie Rendering
function renderMovies() {
    const tbody = document.getElementById('movies-tbody');
    if (!tbody) return;

    if (filteredMovies.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading-row">No movies found matching the filter criteria.</td></tr>';
        return;
    }

    const rows = filteredMovies.map(movie => {
        const genres = Array.isArray(movie.genres) 
            ? movie.genres.join(', ') 
            : movie.genres || 'N/A';
        
        return `
            <tr>
                <td>${escapeHtml(movie.title || 'Unknown')}</td>
                <td>${movie.runtime_minutes || '?'} m</td>
                <td>${movie.year || 'N/A'}</td>
                <td>${movie.vote_average ? movie.vote_average.toFixed(1) : 'N/A'}</td>
                <td>${escapeHtml(movie.certification || 'N/A')}</td>
                <td>${escapeHtml(genres)}</td>
            </tr>
        `;
    }).join('');

    tbody.innerHTML = rows;
}

// Filtering
function applyRuntimeFilters() {
    const minRuntime = parseInt(document.getElementById('min-runtime').value) || 0;
    const maxRuntime = parseInt(document.getElementById('max-runtime').value) || Infinity;
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

    filteredMovies = allMovies.filter(movie => {
        const runtime = movie.runtime_minutes || 0;
        return runtime >= minRuntime && runtime <= maxRuntime;
    });

    sortMovies();
    renderMovies();
    updateFilterResults();
}

function resetFilters() {
    document.getElementById('min-runtime').value = 90;
    document.getElementById('max-runtime').value = 160;
    
    // Clear any error message
    const errorElement = document.getElementById('filter-error');
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.classList.remove('show');
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
            aVal = parseFloat(aVal) || 0;
            bVal = parseFloat(bVal) || 0;
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
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
