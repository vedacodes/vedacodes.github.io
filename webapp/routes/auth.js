const express = require('express');
const session = require('express-session');
const Keycloak = require('keycloak-connect');
const database = require('../models/database');

const router = express.Router();

// Keycloak configuration
const keycloakConfig = {
    'realm': process.env.KEYCLOAK_REALM || 'vedablog',
    'auth-server-url': process.env.KEYCLOAK_URL || 'http://keycloak:8080',
    'ssl-required': 'external',
    'resource': process.env.KEYCLOAK_CLIENT_ID || 'vedablog-client',
    'public-client': true,
    'confidential-port': 0
};

// Create a session store for Keycloak
const memoryStore = new session.MemoryStore();

// Initialize Keycloak
const keycloak = new Keycloak({ store: memoryStore }, keycloakConfig);

// Middleware to add user information to requests
async function addUserInfo(req, res, next) {
    if (req.kauth && req.kauth.grant && req.kauth.grant.access_token) {
        try {
            const token = req.kauth.grant.access_token;
            const userId = token.content.sub;
            
            // Get or create user preferences
            let userPrefs = await database.userPreferences.findByKeycloakId(userId);
            if (!userPrefs) {
                userPrefs = await database.userPreferences.create({
                    keycloak_user_id: userId,
                    display_name: token.content.preferred_username || token.content.name,
                    profile_picture_url: null,
                    email_notifications: true
                });
            }
            
            req.user = {
                id: userId,
                username: token.content.preferred_username,
                email: token.content.email,
                name: token.content.name,
                preferences: userPrefs
            };
        } catch (error) {
            console.error('Error adding user info:', error);
        }
    }
    next();
}

// Login route
router.get('/login', keycloak.protect(), (req, res) => {
    res.redirect('/');
});

// Logout route
router.get('/logout', (req, res) => {
    if (req.kauth && req.kauth.grant) {
        req.kauth.logout();
    }
    req.session.destroy((err) => {
        if (err) {
            console.error('Session destruction error:', err);
        }
        res.redirect('/');
    });
});

// Profile route
router.get('/profile', keycloak.protect(), addUserInfo, async (req, res) => {
    try {
        const favorites = await database.favorites.findByUser(req.user.id);
        res.render('pages/profile', {
            title: 'My Profile',
            user: req.user,
            favorites: favorites
        });
    } catch (error) {
        console.error('Profile error:', error);
        res.status(500).render('pages/error', {
            title: 'Error',
            user: req.user,
            error: { status: 500, message: 'Failed to load profile' }
        });
    }
});

// Update profile route
router.post('/profile', keycloak.protect(), addUserInfo, async (req, res) => {
    try {
        const { display_name, email_notifications } = req.body;
        
        await database.userPreferences.update(req.user.id, {
            display_name: display_name || req.user.preferences.display_name,
            profile_picture_url: req.user.preferences.profile_picture_url,
            email_notifications: email_notifications === 'on'
        });
        
        res.redirect('/auth/profile?updated=true');
    } catch (error) {
        console.error('Profile update error:', error);
        res.status(500).render('pages/error', {
            title: 'Error',
            user: req.user,
            error: { status: 500, message: 'Failed to update profile' }
        });
    }
});

// Dashboard route
router.get('/dashboard', keycloak.protect(), addUserInfo, async (req, res) => {
    try {
        const favorites = await database.favorites.findByUser(req.user.id);
        res.render('pages/dashboard', {
            title: 'My Dashboard',
            user: req.user,
            favorites: favorites
        });
    } catch (error) {
        console.error('Dashboard error:', error);
        res.status(500).render('pages/error', {
            title: 'Error',
            user: req.user,
            error: { status: 500, message: 'Failed to load dashboard' }
        });
    }
});

// Export both router and middleware
module.exports = {
    router,
    keycloak,
    addUserInfo
};