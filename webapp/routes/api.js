const express = require('express');
const rateLimit = require('express-rate-limit');
const database = require('../models/database');
const { keycloak, addUserInfo } = require('./auth');

const router = express.Router();

// Rate limiting for API endpoints
const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    message: 'Too many API requests from this IP, please try again later.'
});

const strictLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 20, // limit each IP to 20 requests per windowMs
    message: 'Too many requests from this IP, please try again later.'
});

router.use(apiLimiter);
router.use(addUserInfo);

// Get destination details
router.get('/destinations/:slug', async (req, res) => {
    try {
        const destination = await database.destinations.findBySlug(req.params.slug);
        if (!destination) {
            return res.status(404).json({ error: 'Destination not found' });
        }

        const [ratings, favoriteCount] = await Promise.all([
            database.ratings.findByDestination(destination.id),
            database.favorites.getCount(destination.id)
        ]);

        res.json({
            ...destination,
            ratings,
            favoriteCount
        });
    } catch (error) {
        console.error('API destinations error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Search destinations
router.get('/destinations', async (req, res) => {
    try {
        const { q, continent, limit = 20, offset = 0 } = req.query;
        let destinations;

        if (q) {
            destinations = await database.destinations.search(q);
        } else if (continent) {
            destinations = await database.destinations.findByContinent(continent);
        } else {
            destinations = await database.destinations.findAll(parseInt(limit), parseInt(offset));
        }

        res.json({ destinations, total: destinations.length });
    } catch (error) {
        console.error('API search error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Add to favorites (protected route)
router.post('/favorites/:destinationId', strictLimiter, keycloak.protect(), async (req, res) => {
    try {
        const destinationId = parseInt(req.params.destinationId);
        const userId = req.user.id;

        const favorite = await database.favorites.add(userId, destinationId);
        res.json({ success: true, favorite });
    } catch (error) {
        if (error.message === 'Destination already in favorites') {
            return res.status(409).json({ error: error.message });
        }
        console.error('API add favorite error:', error);
        res.status(500).json({ error: 'Failed to add favorite' });
    }
});

// Remove from favorites (protected route)
router.delete('/favorites/:destinationId', strictLimiter, keycloak.protect(), async (req, res) => {
    try {
        const destinationId = parseInt(req.params.destinationId);
        const userId = req.user.id;

        const removed = await database.favorites.remove(userId, destinationId);
        if (!removed) {
            return res.status(404).json({ error: 'Favorite not found' });
        }

        res.json({ success: true });
    } catch (error) {
        console.error('API remove favorite error:', error);
        res.status(500).json({ error: 'Failed to remove favorite' });
    }
});

// Get user favorites (protected route)
router.get('/favorites', keycloak.protect(), async (req, res) => {
    try {
        const favorites = await database.favorites.findByUser(req.user.id);
        res.json({ favorites });
    } catch (error) {
        console.error('API get favorites error:', error);
        res.status(500).json({ error: 'Failed to get favorites' });
    }
});

// Add comment (protected route)
router.post('/comments', strictLimiter, keycloak.protect(), async (req, res) => {
    try {
        const { destination_id, content } = req.body;

        if (!destination_id || !content || content.trim().length < 5) {
            return res.status(400).json({ error: 'Invalid comment data' });
        }

        if (content.length > 1000) {
            return res.status(400).json({ error: 'Comment too long (max 1000 characters)' });
        }

        const comment = await database.comments.create({
            keycloak_user_id: req.user.id,
            destination_id: parseInt(destination_id),
            content: content.trim()
        });

        res.json({ success: true, comment });
    } catch (error) {
        console.error('API add comment error:', error);
        res.status(500).json({ error: 'Failed to add comment' });
    }
});

// Get comments for destination
router.get('/comments/:destinationId', async (req, res) => {
    try {
        const comments = await database.comments.findByDestination(
            parseInt(req.params.destinationId),
            true // only approved comments
        );
        res.json({ comments });
    } catch (error) {
        console.error('API get comments error:', error);
        res.status(500).json({ error: 'Failed to get comments' });
    }
});

// Add/update rating (protected route)
router.post('/ratings', strictLimiter, keycloak.protect(), async (req, res) => {
    try {
        const { destination_id, rating } = req.body;

        if (!destination_id || !rating || rating < 1 || rating > 5) {
            return res.status(400).json({ error: 'Invalid rating data' });
        }

        const ratingRecord = await database.ratings.upsert({
            keycloak_user_id: req.user.id,
            destination_id: parseInt(destination_id),
            rating: parseInt(rating)
        });

        // Get updated ratings
        const updatedRatings = await database.ratings.findByDestination(parseInt(destination_id));

        res.json({ success: true, rating: ratingRecord, aggregateRatings: updatedRatings });
    } catch (error) {
        console.error('API add rating error:', error);
        res.status(500).json({ error: 'Failed to add rating' });
    }
});

// Get ratings for destination
router.get('/ratings/:destinationId', async (req, res) => {
    try {
        const ratings = await database.ratings.findByDestination(parseInt(req.params.destinationId));
        res.json({ ratings });
    } catch (error) {
        console.error('API get ratings error:', error);
        res.status(500).json({ error: 'Failed to get ratings' });
    }
});

// Health check
router.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString() 
    });
});

module.exports = router;