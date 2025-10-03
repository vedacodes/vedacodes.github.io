const { Pool } = require('pg');

// Database configuration
const config = {
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    database: process.env.DB_NAME || 'vedablog',
    user: process.env.DB_USER || 'vedablog',
    password: process.env.DB_PASSWORD || 'vedablog123',
    max: 20, // Maximum number of clients in the pool
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
};

const pool = new Pool(config);

// Handle pool errors
pool.on('error', (err, client) => {
    console.error('Unexpected error on idle client', err);
    process.exit(-1);
});

// Database utility functions
const database = {
    // Test connection
    async testConnection() {
        try {
            const client = await pool.connect();
            const result = await client.query('SELECT NOW()');
            client.release();
            console.log('Database connected successfully at:', result.rows[0].now);
            return true;
        } catch (error) {
            console.error('Database connection failed:', error);
            throw error;
        }
    },

    // Generic query function
    async query(text, params) {
        const start = Date.now();
        try {
            const result = await pool.query(text, params);
            const duration = Date.now() - start;
            console.log('Executed query', { text, duration, rows: result.rowCount });
            return result;
        } catch (error) {
            console.error('Query error:', { text, error: error.message });
            throw error;
        }
    },

    // Transaction wrapper
    async transaction(callback) {
        const client = await pool.connect();
        try {
            await client.query('BEGIN');
            const result = await callback(client);
            await client.query('COMMIT');
            return result;
        } catch (error) {
            await client.query('ROLLBACK');
            throw error;
        } finally {
            client.release();
        }
    },

    // Close pool (for graceful shutdown)
    async close() {
        await pool.end();
    }
};

// User preferences functions
database.userPreferences = {
    async findByKeycloakId(keycloakUserId) {
        const result = await database.query(
            'SELECT * FROM user_preferences WHERE keycloak_user_id = $1',
            [keycloakUserId]
        );
        return result.rows[0];
    },

    async create(userData) {
        const result = await database.query(
            `INSERT INTO user_preferences (keycloak_user_id, display_name, profile_picture_url, email_notifications)
             VALUES ($1, $2, $3, $4) RETURNING *`,
            [userData.keycloak_user_id, userData.display_name, userData.profile_picture_url, userData.email_notifications]
        );
        return result.rows[0];
    },

    async update(keycloakUserId, userData) {
        const result = await database.query(
            `UPDATE user_preferences 
             SET display_name = $2, profile_picture_url = $3, email_notifications = $4, updated_at = CURRENT_TIMESTAMP
             WHERE keycloak_user_id = $1 RETURNING *`,
            [keycloakUserId, userData.display_name, userData.profile_picture_url, userData.email_notifications]
        );
        return result.rows[0];
    }
};

// Destinations functions
database.destinations = {
    async findAll(limit = 50, offset = 0) {
        const result = await database.query(
            'SELECT * FROM destinations ORDER BY featured DESC, title ASC LIMIT $1 OFFSET $2',
            [limit, offset]
        );
        return result.rows;
    },

    async findBySlug(slug) {
        const result = await database.query(
            'SELECT * FROM destinations WHERE slug = $1',
            [slug]
        );
        return result.rows[0];
    },

    async findFeatured() {
        const result = await database.query(
            'SELECT * FROM destinations WHERE featured = true ORDER BY title ASC'
        );
        return result.rows;
    },

    async findByContinent(continent) {
        const result = await database.query(
            'SELECT * FROM destinations WHERE continent = $1 ORDER BY title ASC',
            [continent]
        );
        return result.rows;
    },

    async search(searchTerm) {
        const result = await database.query(
            `SELECT * FROM destinations 
             WHERE title ILIKE $1 OR description ILIKE $1 OR country ILIKE $1
             ORDER BY featured DESC, title ASC`,
            [`%${searchTerm}%`]
        );
        return result.rows;
    }
};

// Favorites functions
database.favorites = {
    async findByUser(keycloakUserId) {
        const result = await database.query(
            `SELECT f.*, d.slug, d.title, d.image_url, d.country 
             FROM favorites f 
             JOIN destinations d ON f.destination_id = d.id 
             WHERE f.keycloak_user_id = $1 
             ORDER BY f.created_at DESC`,
            [keycloakUserId]
        );
        return result.rows;
    },

    async add(keycloakUserId, destinationId) {
        try {
            const result = await database.query(
                'INSERT INTO favorites (keycloak_user_id, destination_id) VALUES ($1, $2) RETURNING *',
                [keycloakUserId, destinationId]
            );
            return result.rows[0];
        } catch (error) {
            if (error.code === '23505') { // Unique constraint violation
                throw new Error('Destination already in favorites');
            }
            throw error;
        }
    },

    async remove(keycloakUserId, destinationId) {
        const result = await database.query(
            'DELETE FROM favorites WHERE keycloak_user_id = $1 AND destination_id = $2 RETURNING *',
            [keycloakUserId, destinationId]
        );
        return result.rows[0];
    },

    async isFavorite(keycloakUserId, destinationId) {
        const result = await database.query(
            'SELECT 1 FROM favorites WHERE keycloak_user_id = $1 AND destination_id = $2',
            [keycloakUserId, destinationId]
        );
        return result.rows.length > 0;
    },

    async getCount(destinationId) {
        const result = await database.query(
            'SELECT COUNT(*) as count FROM favorites WHERE destination_id = $1',
            [destinationId]
        );
        return parseInt(result.rows[0].count);
    }
};

// Comments functions
database.comments = {
    async findByDestination(destinationId, approved = true) {
        const result = await database.query(
            `SELECT c.*, up.display_name 
             FROM comments c 
             LEFT JOIN user_preferences up ON c.keycloak_user_id = up.keycloak_user_id 
             WHERE c.destination_id = $1 AND c.approved = $2 
             ORDER BY c.created_at DESC`,
            [destinationId, approved]
        );
        return result.rows;
    },

    async create(commentData) {
        const result = await database.query(
            'INSERT INTO comments (keycloak_user_id, destination_id, content) VALUES ($1, $2, $3) RETURNING *',
            [commentData.keycloak_user_id, commentData.destination_id, commentData.content]
        );
        return result.rows[0];
    },

    async approve(commentId) {
        const result = await database.query(
            'UPDATE comments SET approved = true WHERE id = $1 RETURNING *',
            [commentId]
        );
        return result.rows[0];
    }
};

// Ratings functions
database.ratings = {
    async findByDestination(destinationId) {
        const result = await database.query(
            'SELECT AVG(rating)::numeric(3,2) as average, COUNT(*) as count FROM ratings WHERE destination_id = $1',
            [destinationId]
        );
        return {
            average: parseFloat(result.rows[0].average) || 0,
            count: parseInt(result.rows[0].count)
        };
    },

    async findUserRating(keycloakUserId, destinationId) {
        const result = await database.query(
            'SELECT rating FROM ratings WHERE keycloak_user_id = $1 AND destination_id = $2',
            [keycloakUserId, destinationId]
        );
        return result.rows[0]?.rating;
    },

    async upsert(ratingData) {
        const result = await database.query(
            `INSERT INTO ratings (keycloak_user_id, destination_id, rating) 
             VALUES ($1, $2, $3) 
             ON CONFLICT (keycloak_user_id, destination_id) 
             DO UPDATE SET rating = $3 
             RETURNING *`,
            [ratingData.keycloak_user_id, ratingData.destination_id, ratingData.rating]
        );
        return result.rows[0];
    }
};

module.exports = database;