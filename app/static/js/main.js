
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initApp();
});

function initApp() {
    // Add event listeners to interactive elements
    setupEventListeners();
    
    // Load initial data if needed
    loadInitialData();
}

function setupEventListeners() {
    // Search functionality
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                performSearch(this.value);
            }
        });
    }
    
    // Movie card interactions
    const movieCards = document.querySelectorAll('.movie-card');
    movieCards.forEach(card => {
        card.addEventListener('click', function() {
            const movieId = this.dataset.id;
            if (movieId) {
                window.location.href = `/movie/${movieId}`;
            }
        });
    });
    
    // Icon buttons interactions
    const iconButtons = document.querySelectorAll('.icon-btn');
    iconButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent triggering card click
            this.classList.toggle('active');
            
            // Change icon based on action
            const icon = this.querySelector('i');
            if (icon.classList.contains('far')) {
                icon.classList.replace('far', 'fas');
            } else {
                icon.classList.replace('fas', 'far');
            }
        });
    });
}

function performSearch(query) {
    if (query.trim() !== '') {
        // In a real application, this would make an API call
        console.log(`Searching for: ${query}`);
        // window.location.href = `/search?q=${encodeURIComponent(query)}`;
        alert(`Search functionality would search for: ${query}`);
    }
}

function loadInitialData() {
    // This function would load initial data from the API
    // For now, we're using static data in the templates
    console.log('Application initialized');
}

// Utility function to format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Utility function to handle API errors
function handleApiError(error) {
    console.error('API Error:', error);
    alert('An error occurred. Please try again later.');
}