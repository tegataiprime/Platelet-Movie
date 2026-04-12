// ===== Theme Management =====
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// ===== Data Loading =====
let movieData = [];
let currentSort = { column: null, direction: 'asc' };

async function loadData() {
    try {
        const response = await fetch('data.json');
        const data = await response.json();
        
        movieData = data.movies || [];
        renderMovies(movieData);
        renderCommentary(data.commentary || '');
        renderLastUpdated(data.generated_at || '');
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('movie-tbody').innerHTML = `
            <tr><td colspan="6" class="loading">Error loading movie data. Please try again later.</td></tr>
        `;
        document.querySelector('.commentary-content').innerHTML = `
            <p class="loading">Error loading commentary.</p>
        `;
    }
}

// ===== Rendering Functions =====
function renderCommentary(commentary) {
    const container = document.querySelector('.commentary-content');
    if (!commentary) {
        container.innerHTML = '<p>No commentary available this week.</p>';
        return;
    }
    
    // Split by paragraphs and wrap each in <p> tags
    const paragraphs = commentary.split('\n\n')
        .filter(p => p.trim())
        .map(p => `<p>${p.trim()}</p>`)
        .join('');
    
    container.innerHTML = paragraphs;
}

function renderLastUpdated(timestamp) {
    const element = document.getElementById('last-updated');
    if (!timestamp) {
        element.textContent = '';
        return;
    }
    
    const date = new Date(timestamp);
    const formatted = date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
    element.textContent = `Last updated: ${formatted}`;
}

function renderMovies(movies) {
    const tbody = document.getElementById('movie-tbody');
    
    if (!movies || movies.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">No movies found.</td></tr>';
        return;
    }
    
    tbody.innerHTML = movies.map(movie => {
        const rating = movie.rating != null ? movie.rating.toFixed(1) : 'N/A';
        const certification = movie.certification || 'NR';
        const year = movie.year != null ? movie.year : 'N/A';
        const genres = movie.genres && movie.genres.length > 0 
            ? movie.genres.join(', ') 
            : 'N/A';
        
        return `
            <tr>
                <td>${movie.runtime_minutes} min</td>
                <td>${year}</td>
                <td>${rating}</td>
                <td>${certification}</td>
                <td>${genres}</td>
                <td>${movie.title}</td>
            </tr>
        `;
    }).join('');
}

// ===== Sorting Functions =====
function sortMovies(column) {
    // Determine sort direction
    if (currentSort.column === column) {
        // Toggle direction if same column
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        // Default to ascending for new column
        currentSort.column = column;
        currentSort.direction = 'asc';
    }
    
    // Sort the data
    const sortedMovies = [...movieData].sort((a, b) => {
        let aVal, bVal;
        
        switch (column) {
            case 'runtime':
                aVal = a.runtime_minutes;
                bVal = b.runtime_minutes;
                break;
            case 'year':
                aVal = a.year != null ? a.year : -1;
                bVal = b.year != null ? b.year : -1;
                break;
            case 'score':
                aVal = a.rating != null ? a.rating : -1;
                bVal = b.rating != null ? b.rating : -1;
                break;
            case 'rated':
                aVal = a.certification || '';
                bVal = b.certification || '';
                break;
            case 'genres':
                aVal = a.genres && a.genres.length > 0 ? a.genres[0] : '';
                bVal = b.genres && b.genres.length > 0 ? b.genres[0] : '';
                break;
            case 'title':
                aVal = a.title;
                bVal = b.title;
                break;
            default:
                return 0;
        }
        
        // Compare values
        let comparison = 0;
        if (typeof aVal === 'string') {
            comparison = aVal.localeCompare(bVal);
        } else {
            comparison = aVal - bVal;
        }
        
        return currentSort.direction === 'asc' ? comparison : -comparison;
    });
    
    // Update UI
    renderMovies(sortedMovies);
    updateSortIndicators();
}

function updateSortIndicators() {
    // Remove all sort classes
    document.querySelectorAll('th.sortable').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Add class to current sorted column
    if (currentSort.column) {
        const th = document.querySelector(`th[data-sort="${currentSort.column}"]`);
        if (th) {
            th.classList.add(`sort-${currentSort.direction}`);
        }
    }
}

// ===== Event Listeners =====
function setupEventListeners() {
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Sortable table headers
    document.querySelectorAll('th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const column = th.getAttribute('data-sort');
            sortMovies(column);
        });
    });
}

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    setupEventListeners();
    loadData();
});
