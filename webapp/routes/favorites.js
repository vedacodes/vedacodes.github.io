const express = require('express');
const database = require('../models/database');
const { keycloak, addUserInfo } = require('./auth');

const router = express.Router();

// Apply authentication middleware to all routes
router.use(keycloak.protect());
router.use(addUserInfo);

// Show favorites page
router.get('/', async (req, res) => {
    try {
        const favorites = await database.favorites.findByUser(req.user.id);
        
        res.render('pages/favorites', {
            title: 'My Favorites',
            user: req.user,
            favorites
        });
    } catch (error) {
        console.error('Favorites page error:', error);
        res.status(500).render('pages/error', {
            title: 'Error',
            user: req.user,
            error: { status: 500, message: 'Failed to load favorites' }
        });
    }
});

module.exports = router;