const express = require('express');
const session = require('express-session');
const database = require('../models/database');

const router = express.Router();

// Middleware to add user information to requests
async function addUserInfo(req, res, next) {
    if (req.session && req.session.user) {
        req.user = req.session.user;
    }
    next();
}

// Login route - redirect to Keycloak
router.get('/login', (req, res) => {
    const keycloakLoginUrl = `http://localhost:8081/realms/vedablog/protocol/openid-connect/auth?client_id=vedablog-client&redirect_uri=${encodeURIComponent('http://localhost:3000/auth/callback')}&response_type=code&scope=openid`;
    res.redirect(keycloakLoginUrl);
});

// Callback route to handle Keycloak response
router.get('/callback', async (req, res) => {
    const { code, state } = req.query;
    
    if (!code) {
        return res.status(400).send('Authorization code missing');
    }
    
    try {
        // Exchange code for token
        const tokenResponse = await fetch('http://keycloak:8080/realms/vedablog/protocol/openid-connect/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                grant_type: 'authorization_code',
                client_id: 'vedablog-client',
                code: code,
                redirect_uri: 'http://localhost:3000/auth/callback'
            })
        });
        
        if (!tokenResponse.ok) {
            throw new Error(`Token exchange failed: ${tokenResponse.status}`);
        }
        
        const tokens = await tokenResponse.json();
        
        // Decode the access token to get user info
        const tokenParts = tokens.access_token.split('.');
        const payload = JSON.parse(Buffer.from(tokenParts[1], 'base64').toString());
        
        // Store user session
        req.session.user = {
            id: payload.sub,
            username: payload.preferred_username,
            email: payload.email,
            name: payload.name,
            accessToken: tokens.access_token
        };
        
        // Create/update user preferences in database
        let userPrefs = await database.userPreferences.findByKeycloakId(payload.sub);
        if (!userPrefs) {
            userPrefs = await database.userPreferences.create({
                keycloak_user_id: payload.sub,
                display_name: payload.preferred_username || payload.name,
                profile_picture_url: null,
                email_notifications: true
            });
        }
        
        req.session.user.preferences = userPrefs;
        
        // Redirect to home page
        res.redirect('/?login=success');
        
    } catch (error) {
        console.error('Authentication callback error:', error);
        res.status(500).send('Authentication failed');
    }
});

// Logout route
router.get('/logout', (req, res) => {
    req.session.destroy((err) => {
        if (err) {
            console.error('Session destruction error:', err);
        }
        const logoutUrl = `http://localhost:8081/realms/vedablog/protocol/openid-connect/logout?redirect_uri=${encodeURIComponent('http://localhost:3000/?logout=success')}`;
        res.redirect(logoutUrl);
    });
});

// Simple authentication middleware
function requireAuth(req, res, next) {
    if (!req.session || !req.session.user) {
        return res.redirect('/auth/login');
    }
    next();
}

// Profile route
router.get('/profile', requireAuth, addUserInfo, async (req, res) => {
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
router.post('/profile', requireAuth, addUserInfo, async (req, res) => {
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
router.get('/dashboard', requireAuth, addUserInfo, async (req, res) => {
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
    addUserInfo,
    requireAuth
};