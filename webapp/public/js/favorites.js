// Favorites functionality

document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if user is logged in
    if (window.userData) {
        initializeFavorites();
    }
});

function initializeFavorites() {
    // Add event listeners to all favorite buttons
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    favoriteButtons.forEach(button => {
        button.addEventListener('click', handleFavoriteToggle);
    });
    
    // Load existing favorites
    loadUserFavorites();
}

function handleFavoriteToggle(e) {
    e.stopPropagation();
    
    if (!window.auth.requireAuth()) {
        return;
    }
    
    const button = e.currentTarget;
    const destinationId = button.dataset.destinationId;
    const icon = button.querySelector('i');
    const isCurrentlyFavorite = button.classList.contains('active');
    
    // Optimistic UI update
    button.disabled = true;
    
    if (isCurrentlyFavorite) {
        removeFavorite(destinationId, button, icon);
    } else {
        addFavorite(destinationId, button, icon);
    }
}

function addFavorite(destinationId, button, icon) {
    fetch(`/api/favorites/${destinationId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Failed to add favorite');
    })
    .then(data => {
        // Update UI
        button.classList.add('active');
        icon.className = 'fas fa-heart';
        button.dataset.tooltip = 'Remove from favorites';
        
        window.utils.showNotification('Added to favorites!', 'success');
        updateFavoritesCount(1);
    })
    .catch(error => {
        console.error('Add favorite error:', error);
        window.utils.showNotification('Failed to add to favorites. Please try again.', 'error');
    })
    .finally(() => {
        button.disabled = false;
    });
}

function removeFavorite(destinationId, button, icon) {
    fetch(`/api/favorites/${destinationId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Failed to remove favorite');
    })
    .then(data => {
        // Update UI
        button.classList.remove('active');
        icon.className = 'far fa-heart';
        button.dataset.tooltip = 'Add to favorites';
        
        window.utils.showNotification('Removed from favorites!', 'info');
        updateFavoritesCount(-1);
    })
    .catch(error => {
        console.error('Remove favorite error:', error);
        window.utils.showNotification('Failed to remove from favorites. Please try again.', 'error');
    })
    .finally(() => {
        button.disabled = false;
    });
}

function loadUserFavorites() {
    fetch('/api/favorites')
        .then(response => response.json())
        .then(data => {
            // Mark favorite destinations
            data.favorites.forEach(favorite => {
                const favoriteButtons = document.querySelectorAll(`[data-destination-id="${favorite.destination_id}"] .favorite-btn`);
                favoriteButtons.forEach(button => {
                    button.classList.add('active');
                    const icon = button.querySelector('i');
                    if (icon) {
                        icon.className = 'fas fa-heart';
                    }
                    button.dataset.tooltip = 'Remove from favorites';
                });
            });
            
            // Update favorites count in navigation
            updateFavoritesCountDisplay(data.favorites.length);
        })
        .catch(error => {
            console.error('Error loading user favorites:', error);
        });
}

function updateFavoritesCount(delta) {
    const countElement = document.getElementById('userFavoritesCount');
    if (countElement) {
        const currentCount = parseInt(countElement.textContent) || 0;
        const newCount = Math.max(0, currentCount + delta);
        countElement.textContent = newCount;
    }
}

function updateFavoritesCountDisplay(count) {
    const countElement = document.getElementById('userFavoritesCount');
    if (countElement) {
        countElement.textContent = count;
    }
}

// Bulk operations for favorites page
function removeAllFavorites() {
    if (!confirm('Are you sure you want to remove all favorites? This action cannot be undone.')) {
        return;
    }
    
    const favoriteCards = document.querySelectorAll('.favorite-card');
    const promises = [];
    
    favoriteCards.forEach(card => {
        const destinationId = card.dataset.destinationId;
        if (destinationId) {
            promises.push(
                fetch(`/api/favorites/${destinationId}`, { method: 'DELETE' })
                    .then(response => {
                        if (response.ok) {
                            card.remove();
                        }
                    })
            );
        }
    });
    
    Promise.all(promises)
        .then(() => {
            window.utils.showNotification('All favorites removed successfully!', 'success');
            updateFavoritesCountDisplay(0);
            
            // Show empty state if no favorites left
            const favoritesContainer = document.querySelector('.favorites-grid');
            if (favoritesContainer && favoritesContainer.children.length === 0) {
                showEmptyFavoritesState();
            }
        })
        .catch(error => {
            console.error('Error removing all favorites:', error);
            window.utils.showNotification('Failed to remove some favorites. Please try again.', 'error');
        });
}

function showEmptyFavoritesState() {
    const container = document.querySelector('.favorites-container');
    if (container) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">
                    <i class="far fa-heart"></i>
                </div>
                <h3>No Favorites Yet</h3>
                <p>Start exploring destinations and add them to your favorites!</p>
                <a href="/" class="cta-btn primary">
                    <i class="fas fa-compass"></i>
                    Explore Destinations
                </a>
            </div>
        `;
    }
}

// Export for global use
window.favorites = {
    addFavorite,
    removeFavorite,
    removeAllFavorites,
    loadUserFavorites
};