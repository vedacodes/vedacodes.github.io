# Dynamic Travel Blog Architecture Plan

## Overview
Transform the static Veda's Travel Diary website into a dynamic platform with user authentication, favorites functionality, and user engagement features using open-source tools deployed on AWS EC2 with Docker containers.

## Current State Analysis
- **Current Setup**: Static HTML/CSS website hosted on GitHub Pages
- **Content**: Travel blog with destination pages (30+ cities)
- **Structure**: Individual HTML pages per destination with shared CSS styling
- **Deployment**: Basic Nginx Docker container

## Target Architecture

### 1. Infrastructure Overview
```
┌─────────────────────────────────────────────────────────────┐
│                        AWS EC2 Instance                     │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   Web App       │ │   Keycloak      │ │   PostgreSQL    ││
│  │  (Node.js +     │ │ (Authentication │ │   Database      ││
│  │   Express)      │ │    Server)      │ │                 ││
│  │   Port: 3000    │ │   Port: 8080    │ │   Port: 5432    ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
│           │                    │                    │       │
│  ┌─────────────────────────────────────────────────────────┐│
│  │               Nginx Reverse Proxy                       ││
│  │                   Port: 80/443                          ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 2. Technology Stack (All Open Source)

#### Frontend
- **Base**: Existing HTML/CSS/JavaScript (preserved)
- **Enhancement**: Vanilla JavaScript for dynamic features
- **CSS Framework**: Keep existing custom styling
- **Authentication UI**: Keycloak JavaScript adapter

#### Backend
- **Runtime**: Node.js with Express.js
- **Template Engine**: EJS (to render existing HTML content)
- **Session Management**: Express-session with Redis (optional)
- **API**: RESTful endpoints for user interactions

#### Authentication
- **Identity Provider**: Keycloak (Open Source IAM)
- **Protocols**: OpenID Connect / OAuth 2.0
- **Features**: User registration, login, password reset, social login

#### Database
- **Primary DB**: PostgreSQL (user data, favorites, interactions)
- **Schema**: User profiles, favorites, comments, ratings
- **Connection**: pg (Node.js PostgreSQL client)

#### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **SSL**: Let's Encrypt (Certbot)
- **Monitoring**: Docker logs + optional Prometheus/Grafana

### 3. Database Schema

#### Users Table (managed by Keycloak)
- Keycloak handles user authentication and basic profile data

#### User Preferences Table
```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    keycloak_user_id UUID NOT NULL UNIQUE,
    display_name VARCHAR(100),
    profile_picture_url TEXT,
    email_notifications BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Destinations Table
```sql
CREATE TABLE destinations (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'barcelona', 'paris'
    title VARCHAR(200) NOT NULL,
    description TEXT,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Favorites Table
```sql
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    keycloak_user_id UUID NOT NULL,
    destination_id INTEGER REFERENCES destinations(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(keycloak_user_id, destination_id)
);
```

#### Comments Table
```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    keycloak_user_id UUID NOT NULL,
    destination_id INTEGER REFERENCES destinations(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Ratings Table
```sql
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    keycloak_user_id UUID NOT NULL,
    destination_id INTEGER REFERENCES destinations(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(keycloak_user_id, destination_id)
);
```

### 4. New Features to Implement

#### Phase 1: Core Authentication & Favorites
1. **User Authentication**
   - Login/Logout via Keycloak
   - User profile management
   - Session management

2. **Favorites System**
   - Heart icon on each destination page
   - Favorites dashboard for logged-in users
   - Favorite count display

3. **User Dashboard**
   - Personal favorites list
   - Profile management
   - Settings page

#### Phase 2: Enhanced Engagement
1. **Comments System**
   - Add comments to destination pages
   - Comment moderation (simple approval system)
   - Reply to comments

2. **Rating System**
   - 5-star rating for destinations
   - Average rating display
   - Rating-based sorting

3. **User-Generated Content**
   - User photo uploads for destinations
   - Travel tips submission
   - User trip reports

#### Phase 3: Advanced Features
1. **Social Features**
   - User profiles (public/private)
   - Follow other travelers
   - Share favorite destinations

2. **Recommendations**
   - Recommend destinations based on favorites
   - "Similar destinations" suggestions
   - Popular destinations dashboard

3. **Search & Filtering**
   - Search destinations
   - Filter by continent, rating, favorites
   - Advanced search with tags

### 5. File Structure Migration

#### Current Structure Preserved
```
/
├── index.html (enhanced with auth)
├── styles.css (preserved)
├── {destination}-page.html (converted to templates)
├── {destination}-image.jpg (preserved)
└── ...
```

#### New Structure
```
/
├── docker-compose.yml
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf
├── webapp/
│   ├── Dockerfile
│   ├── package.json
│   ├── server.js
│   ├── routes/
│   │   ├── auth.js
│   │   ├── destinations.js
│   │   ├── favorites.js
│   │   └── api.js
│   ├── views/
│   │   ├── layouts/
│   │   │   └── main.ejs
│   │   ├── pages/
│   │   │   ├── index.ejs
│   │   │   ├── destination.ejs
│   │   │   ├── dashboard.ejs
│   │   │   └── profile.ejs
│   │   └── partials/
│   │       ├── header.ejs
│   │       ├── nav.ejs
│   │       └── footer.ejs
│   ├── public/
│   │   ├── css/
│   │   │   └── styles.css (migrated)
│   │   ├── js/
│   │   │   ├── auth.js
│   │   │   ├── favorites.js
│   │   │   └── main.js
│   │   └── images/ (all existing images)
│   └── models/
│       ├── database.js
│       ├── User.js
│       ├── Destination.js
│       └── Favorite.js
├── keycloak/
│   ├── Dockerfile
│   └── realm-config.json
└── database/
    ├── Dockerfile
    ├── init.sql
    └── docker-entrypoint-initdb.d/
```

### 6. Docker Setup

#### docker-compose.yml
```yaml
version: '3.8'
services:
  nginx:
    build: ./nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/etc/ssl
    depends_on:
      - webapp
      - keycloak

  webapp:
    build: ./webapp
    environment:
      - DB_HOST=postgres
      - DB_USER=vedablog
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=vedablog
      - KEYCLOAK_URL=http://keycloak:8080
      - SESSION_SECRET=${SESSION_SECRET}
    depends_on:
      - postgres
      - keycloak
    volumes:
      - ./webapp/public/images:/app/public/images

  keycloak:
    image: quay.io/keycloak/keycloak:latest
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://postgres:5432/keycloak
      - KC_DB_USERNAME=keycloak
      - KC_DB_PASSWORD=${KEYCLOAK_DB_PASSWORD}
    command: start-dev
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### 7. Implementation Phases

#### Phase 1: Infrastructure Setup (Week 1)
1. Set up AWS EC2 instance
2. Configure Docker and Docker Compose
3. Set up PostgreSQL database
4. Configure Keycloak
5. Set up Nginx reverse proxy
6. Implement SSL with Let's Encrypt

#### Phase 2: Core Migration (Week 2)
1. Create Node.js Express application
2. Convert HTML pages to EJS templates
3. Implement authentication integration
4. Create database models and connections
5. Implement favorites functionality

#### Phase 3: Enhanced Features (Week 3)
1. Implement user dashboard
2. Add comments system
3. Implement rating system
4. Add search and filtering

#### Phase 4: Polish and Deploy (Week 4)
1. Implement responsive design improvements
2. Add monitoring and logging
3. Performance optimization
4. Security hardening
5. Final testing and deployment

### 8. Security Considerations

#### Authentication Security
- Keycloak handles password policies
- HTTPS everywhere with SSL certificates
- Secure session management
- CSRF protection

#### Data Security
- Input validation and sanitization
- SQL injection prevention with parameterized queries
- XSS prevention
- Rate limiting on API endpoints

#### Infrastructure Security
- Docker container security best practices
- Firewall configuration (only necessary ports open)
- Regular security updates
- Database access restrictions

### 9. Cost Estimation (AWS EC2)

#### Monthly Costs (Approximate)
- **EC2 t3.medium instance**: $30-40/month
- **EBS storage (50GB)**: $5/month
- **Data transfer**: $5-10/month
- **Total**: ~$40-55/month

#### Alternative Cost-Effective Options
- **EC2 t3.small**: $15-20/month (for lighter traffic)
- **Oracle Cloud Free Tier**: Free (4 ARM cores, 24GB RAM)
- **Google Cloud Free Tier**: $0-300 credits for first year

### 10. Backup and Monitoring Strategy

#### Backup
- Daily PostgreSQL database backups to S3
- Docker volume backups
- Configuration file versioning in Git

#### Monitoring
- Docker container health checks
- Database connection monitoring
- Application error logging
- Basic uptime monitoring

### 11. Migration Strategy

#### Data Migration
1. Extract destination data from existing HTML files
2. Create destination records in database
3. Preserve all existing URLs (SEO friendly)
4. Implement redirects if URL structure changes

#### Content Preservation
- All existing styling preserved
- All images remain accessible
- Existing content structure maintained
- Progressive enhancement approach

### 12. Development Environment Setup

#### Local Development
```bash
# Clone repository
git clone <repo-url>
cd vedacodes.github.io

# Set up environment variables
cp .env.example .env
# Edit .env with local configuration

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Access application
# Web app: http://localhost:3000
# Keycloak: http://localhost:8080
# Database: localhost:5432
```

### 13. Deployment Checklist

#### Pre-deployment
- [ ] EC2 instance configured
- [ ] Domain name configured
- [ ] SSL certificates obtained
- [ ] Environment variables set
- [ ] Database initialized
- [ ] Keycloak realm configured

#### Deployment
- [ ] Deploy Docker containers
- [ ] Configure Nginx
- [ ] Test authentication flow
- [ ] Verify database connections
- [ ] Test all features

#### Post-deployment
- [ ] Monitor application health
- [ ] Set up automated backups
- [ ] Configure log rotation
- [ ] Performance testing
- [ ] Security audit

## Next Steps

1. **Immediate**: Set up local development environment
2. **Week 1**: Provision AWS infrastructure
3. **Week 2**: Begin core application development
4. **Week 3**: Implement user features
5. **Week 4**: Deploy and test production environment

## Resources and Documentation

### Technical Documentation
- [Keycloak Documentation](https://www.keycloak.org/docs/latest/)
- [Express.js Guide](https://expressjs.com/en/guide/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

### Tutorials and Guides
- Keycloak Node.js integration
- Express.js authentication patterns
- Docker deployment on AWS EC2
- Nginx reverse proxy configuration

This plan provides a comprehensive roadmap to transform your static travel blog into a dynamic, user-interactive platform while maintaining all existing content and design, using only free and open-source technologies.