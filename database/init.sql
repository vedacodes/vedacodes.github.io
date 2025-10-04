-- Initialize databases and users
CREATE DATABASE keycloak;
CREATE DATABASE vedablog;

-- Create users
CREATE USER keycloak WITH PASSWORD 'keycloak123';
CREATE USER vedablog WITH PASSWORD 'vedablog123';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;
GRANT ALL PRIVILEGES ON DATABASE vedablog TO vedablog;

-- Connect to keycloak database and set up permissions
\c keycloak;
GRANT ALL ON SCHEMA public TO keycloak;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO keycloak;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO keycloak;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO keycloak;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO keycloak;

-- Connect to vedablog database to create tables
\c vedablog;

-- Create tables for the application
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    keycloak_user_id UUID NOT NULL UNIQUE,
    display_name VARCHAR(100),
    profile_picture_url TEXT,
    email_notifications BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS destinations (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    image_url TEXT,
    content_path TEXT,
    country VARCHAR(100),
    continent VARCHAR(50),
    featured BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    keycloak_user_id UUID NOT NULL,
    destination_id INTEGER REFERENCES destinations(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(keycloak_user_id, destination_id)
);

CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    keycloak_user_id UUID NOT NULL,
    destination_id INTEGER REFERENCES destinations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    approved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ratings (
    id SERIAL PRIMARY KEY,
    keycloak_user_id UUID NOT NULL,
    destination_id INTEGER REFERENCES destinations(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(keycloak_user_id, destination_id)
);

-- Insert initial destination data
INSERT INTO destinations (slug, title, description, image_url, country, continent, featured) VALUES
('barcelona', 'Barcelona - Catalan Capital', 'The vibrant capital of Catalonia, known for its unique architecture, beaches, and culture.', 'barcelona-image.jpg', 'Spain', 'Europe', true),
('paris', 'Paris - City of Light', 'The romantic capital of France, famous for its art, fashion, and cuisine.', 'paris-image.jpg', 'France', 'Europe', true),
('rome', 'Rome - Eternal City', 'The historic capital of Italy, home to ancient ruins and Vatican City.', 'rome-image.jpg', 'Italy', 'Europe', true),
('amsterdam', 'Amsterdam - Venice of the North', 'The charming capital of Netherlands with its canals and liberal culture.', 'amsterdam-image.jpg', 'Netherlands', 'Europe', false),
('athens', 'Athens - Cradle of Democracy', 'The ancient capital of Greece, birthplace of democracy and philosophy.', 'athens-image.jpg', 'Greece', 'Europe', false),
('bangkok', 'Bangkok - City of Angels', 'The bustling capital of Thailand, known for its temples and street food.', 'bangkok-image.jpg', 'Thailand', 'Asia', true),
('berlin', 'Berlin - City of History', 'The capital of Germany, rich in history and modern culture.', 'berlin-image.jpg', 'Germany', 'Europe', false),
('brussels', 'Brussels - Heart of Europe', 'The capital of Belgium and the European Union.', 'brussels-image.jpg', 'Belgium', 'Europe', false),
('cancun', 'Cancun - Tropical Paradise', 'A resort city on the Yucatan Peninsula in Mexico.', 'cancun-image.jpg', 'Mexico', 'North America', true),
('cusco', 'Cusco - Gateway to Machu Picchu', 'The historic capital of the Inca Empire in Peru.', 'cusco-image.jpg', 'Peru', 'South America', true),
('darjeeling', 'Darjeeling - Queen of Hills', 'A hill station in West Bengal, India, famous for its tea.', 'darjeeling-image.jpg', 'India', 'Asia', false),
('gangtok', 'Gangtok - Gateway to the Himalayas', 'The capital of Sikkim, nestled in the Himalayas.', 'gangtok-image.jpg', 'India', 'Asia', false),
('grandcanyon', 'Grand Canyon - Natural Wonder', 'One of the most spectacular natural formations in the United States.', 'grandcanyon-image.jpg', 'United States', 'North America', true),
('interlaken', 'Interlaken - Adventure Capital', 'A resort town in the Swiss Alps, perfect for outdoor activities.', 'interlaken-image.jpg', 'Switzerland', 'Europe', true),
('lasvegas', 'Las Vegas - Entertainment Capital', 'The gambling and entertainment capital of the world.', 'lasvegas-image.jpg', 'United States', 'North America', true),
('lima', 'Lima - Culinary Capital', 'The capital of Peru, known for its gastronomy and colonial architecture.', 'lima-image.jpg', 'Peru', 'South America', false),
('losangeles', 'Los Angeles - City of Angels', 'The entertainment capital of the world, home to Hollywood.', 'losangeles-image.jpg', 'United States', 'North America', true),
('machupicchu', 'Machu Picchu - Lost City of Incas', 'The ancient Incan citadel in the Andes Mountains of Peru.', 'machupicchu-image.jpg', 'Peru', 'South America', true),
('mexicocity', 'Mexico City - Cultural Heart', 'The vibrant capital of Mexico, rich in history and culture.', 'mexicocity-image.jpg', 'Mexico', 'North America', false),
('miami', 'Miami - Magic City', 'A coastal metropolis in Florida known for its beaches and nightlife.', 'miami-image.jpg', 'United States', 'North America', true),
('milan', 'Milan - Fashion Capital', 'The fashion and design capital of Italy.', 'milan-image.jpg', 'Italy', 'Europe', false),
('pattaya', 'Pattaya - Beach Resort', 'A popular beach resort city in Thailand.', 'pattaya-page.html', 'Thailand', 'Asia', false),
('prague', 'Prague - City of a Hundred Spires', 'The capital of Czech Republic, known for its medieval architecture.', 'prague-image.jpg', 'Czech Republic', 'Europe', true),
('santorini', 'Santorini - Greek Island Paradise', 'A volcanic island in the Aegean Sea, famous for its sunsets.', 'santorini-image.jpg', 'Greece', 'Europe', true),
('vatican', 'Vatican City - Spiritual Center', 'The smallest country in the world, home to the Pope.', 'vatican-image.jpg', 'Vatican', 'Europe', false),
('venice', 'Venice - Floating City', 'The romantic canal city in northern Italy.', 'venice-image.jpg', 'Italy', 'Europe', true),
('vienna', 'Vienna - Imperial City', 'The elegant capital of Austria, known for its music and architecture.', 'vienna-image.jpg', 'Austria', 'Europe', false);

-- Grant permissions to vedablog user on all tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vedablog;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vedablog;