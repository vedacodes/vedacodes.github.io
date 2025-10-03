const express = require('express');
const path = require('path');
const fs = require('fs').promises;
const database = require('../models/database');
const { addUserInfo } = require('./auth');

const router = express.Router();

// Middleware to add user info to all requests
router.use(addUserInfo);

// Home page
router.get('/', async (req, res) => {
    try {
        const [featuredDestinations, allDestinations] = await Promise.all([
            database.destinations.findFeatured(),
            database.destinations.findAll()
        ]);

        res.render('pages/index', {
            title: "Veda's Travel Diary - Explore the World",
            user: req.user || null,
            featuredDestinations,
            allDestinations
        });
    } catch (error) {
        console.error('Home page error:', error);
        res.status(500).render('pages/error', {
            title: 'Error',
            user: req.user || null,
            error: { status: 500, message: 'Failed to load home page' }
        });
    }
});

// Search destinations
router.get('/search', async (req, res) => {
    try {
        const { q, continent } = req.query;
        let destinations = [];

        if (q) {
            destinations = await database.destinations.search(q);
        } else if (continent) {
            destinations = await database.destinations.findByContinent(continent);
        } else {
            destinations = await database.destinations.findAll();
        }

        res.render('pages/search', {
            title: 'Search Results',
            user: req.user || null,
            destinations,
            searchQuery: q || '',
            continent: continent || ''
        });
    } catch (error) {
        console.error('Search error:', error);
        res.status(500).render('pages/error', {
            title: 'Error',
            user: req.user || null,
            error: { status: 500, message: 'Search failed' }
        });
    }
});

// Destination page
router.get('/:slug-page.html', async (req, res) => {
    try {
        const { slug } = req.params;
        const destination = await database.destinations.findBySlug(slug);

        if (!destination) {
            return res.status(404).render('pages/404', {
                title: 'Destination Not Found',
                user: req.user || null,
                path: req.path
            });
        }

        // Get additional data
        const [comments, ratings, favoriteCount] = await Promise.all([
            database.comments.findByDestination(destination.id),
            database.ratings.findByDestination(destination.id),
            database.favorites.getCount(destination.id)
        ]);

        let isFavorite = false;
        let userRating = null;

        if (req.user) {
            [isFavorite, userRating] = await Promise.all([
                database.favorites.isFavorite(req.user.id, destination.id),
                database.ratings.findUserRating(req.user.id, destination.id)
            ]);
        }

        // Try to load existing HTML content if available
        let legacyContent = null;
        try {
            const legacyPath = path.join(__dirname, '../../', `${slug}-page.html`);
            const legacyHtml = await fs.readFile(legacyPath, 'utf8');
            
            // Extract the main content (everything between body tags, excluding nav)
            const bodyMatch = legacyHtml.match(/<body[^>]*>(.*?)<\/body>/s);
            if (bodyMatch) {
                let bodyContent = bodyMatch[1];
                // Remove navigation and header elements
                bodyContent = bodyContent.replace(/<nav[^>]*>.*?<\/nav>/gs, '');
                bodyContent = bodyContent.replace(/<div[^>]*class="nav-bar"[^>]*>.*?<\/div>/gs, '');
                legacyContent = bodyContent;
            }
        } catch (error) {
            console.log(`No legacy content found for ${slug}`);
        }

        res.render('pages/destination', {
            title: `${destination.title} | Veda's Travel Diary`,
            user: req.user || null,
            destination,
            comments,
            ratings,
            favoriteCount,
            isFavorite,
            userRating,
            legacyContent
        });
    } catch (error) {
        console.error('Destination page error:', error);
        res.status(500).render('pages/error', {
            title: 'Error',
            user: req.user || null,
            error: { status: 500, message: 'Failed to load destination' }
        });
    }
});

// Legacy URL redirects (without -page.html)
router.get('/:slug', async (req, res) => {
    const { slug } = req.params;
    const destination = await database.destinations.findBySlug(slug);
    
    if (destination) {
        res.redirect(301, `/${slug}-page.html`);
    } else {
        res.status(404).render('pages/404', {
            title: 'Page Not Found',
            user: req.user || null,
            path: req.path
        });
    }
});

module.exports = router;