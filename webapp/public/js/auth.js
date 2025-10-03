// Authentication and user management functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize authentication features
    initializeAuth();
});

function initializeAuth() {
    // Handle login redirects with messages
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('login') === 'success') {
        window.utils.showNotification('Welcome back! You have been logged in successfully.', 'success');
    }
    
    if (urlParams.get('logout') === 'success') {
        window.utils.showNotification('You have been logged out successfully.', 'info');
    }
    
    if (urlParams.get('updated') === 'true') {
        window.utils.showNotification('Your profile has been updated successfully.', 'success');
    }
    
    // Initialize login form if present
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Initialize profile form if present
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileUpdate);
    }
}

function handleLogin(e) {
    e.preventDefault();
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Logging in...';
    submitBtn.disabled = true;
    
    // Redirect to Keycloak login
    window.location.href = '/auth/login';
}

function handleProfileUpdate(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    // Show loading state
    submitBtn.textContent = 'Updating...';
    submitBtn.disabled = true;
    
    fetch('/auth/profile', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            window.utils.showNotification('Profile updated successfully!', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            throw new Error('Failed to update profile');
        }
    })
    .catch(error => {
        console.error('Profile update error:', error);
        window.utils.showNotification('Failed to update profile. Please try again.', 'error');
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

// User authentication utilities
function requireAuth(callback) {
    if (!window.userData) {
        window.utils.showNotification('Please log in to continue.', 'warning');
        setTimeout(() => {
            window.location.href = '/auth/login';
        }, 2000);
        return false;
    }
    
    if (callback && typeof callback === 'function') {
        callback();
    }
    
    return true;
}

function logout() {
    if (confirm('Are you sure you want to log out?')) {
        window.location.href = '/auth/logout';
    }
}

// Export functions for global use
window.auth = {
    requireAuth,
    logout
};