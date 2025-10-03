# Veda's Travel Diary - Dynamic Platform

This is the transformation of the static travel blog into a dynamic platform with user authentication, favorites functionality, and user engagement features.

## 🚀 Quick Start (Development)

### Prerequisites
- Docker and Docker Compose
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vedacodes.github.io
   ```

2. **Start the development environment**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

3. **Access the application**
   - **Web Application**: http://localhost:3000
   - **Keycloak Admin**: http://localhost:8081 (admin/admin123)
   - **Database**: localhost:5433 (postgres/postgres123)

4. **Initial Setup**
   - Wait for all services to start (may take 2-3 minutes)
   - The database will be automatically initialized with destination data
   - Keycloak will need initial realm configuration (see below)

## 🛠️ Architecture

### Services
- **Web App** (Node.js + Express): Main application server
- **Keycloak**: Authentication and user management
- **PostgreSQL**: Database for application data
- **Nginx**: Reverse proxy and static file serving

### Key Features
- ✅ User authentication with Keycloak
- ✅ Favorites system for destinations
- ✅ User dashboard and profile management
- ✅ Comments and rating system (planned)
- ✅ Responsive design with modern UI
- ✅ SEO-friendly URLs preserved
- ✅ Progressive enhancement approach

## 🔧 Configuration

### Keycloak Setup (Required for Authentication)

1. **Access Keycloak Admin Console**
   - URL: http://localhost:8081
   - Username: admin
   - Password: admin123

2. **Create Realm**
   - Create new realm called `vedablog`
   - Or import the realm configuration (if provided)

3. **Create Client**
   - Client ID: `vedablog-client`
   - Client Type: `OpenID Connect`
   - Access Type: `public`
   - Valid Redirect URIs: `http://localhost:3000/*`
   - Web Origins: `http://localhost:3000`

4. **Configure Client Settings**
   - Enable "Standard Flow"
   - Enable "Direct Access Grants"
   - Set logout redirect URI

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key variables:
- `DB_PASSWORD`: PostgreSQL password
- `SESSION_SECRET`: Express session secret (min 32 chars)
- `KEYCLOAK_ADMIN_PASSWORD`: Keycloak admin password

## 📁 Project Structure

```
├── docker-compose.yml          # Production compose file
├── docker-compose.dev.yml      # Development compose file
├── database/
│   └── init.sql               # Database initialization
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf             # Nginx configuration
├── webapp/
│   ├── Dockerfile
│   ├── server.js              # Main application server
│   ├── package.json
│   ├── routes/                # Express routes
│   ├── views/                 # EJS templates
│   ├── public/                # Static assets
│   └── models/                # Database models
└── README.md
```

## 🎯 Development

### Running in Development Mode

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f webapp

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### Making Changes

1. **Backend Changes**: The webapp container will auto-restart on file changes
2. **Frontend Changes**: Static files are served directly, refresh browser
3. **Database Changes**: Modify `database/init.sql` and recreate containers

### Database Management

```bash
# Connect to database
docker exec -it <postgres-container> psql -U postgres -d vedablog

# View tables
\dt

# Example queries
SELECT * FROM destinations;
SELECT * FROM user_preferences;
SELECT * FROM favorites;
```

## 🚢 Deployment

### Production Deployment

1. **Prepare Environment**
   ```bash
   cp .env.example .env
   # Configure production values in .env
   ```

2. **Deploy**
   ```bash
   docker-compose up -d
   ```

3. **Configure SSL** (Production)
   - Update nginx configuration for HTTPS
   - Add SSL certificates to `/ssl` volume
   - Update Keycloak URLs to use HTTPS

### AWS EC2 Deployment

1. **Launch EC2 Instance**
   - Recommended: t3.medium or larger
   - Security groups: HTTP (80), HTTPS (443), SSH (22)

2. **Install Docker**
   ```bash
   sudo yum update -y
   sudo yum install -y docker
   sudo service docker start
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Deploy Application**
   ```bash
   git clone <repository-url>
   cd vedacodes.github.io
   cp .env.example .env
   # Configure .env with production values
   docker-compose up -d
   ```

## 🔒 Security

### Production Security Checklist

- [ ] Change all default passwords
- [ ] Use secure session secrets (32+ chars)
- [ ] Configure HTTPS with valid SSL certificates
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Database backup strategy
- [ ] Rate limiting configuration
- [ ] Content Security Policy headers

## 📊 Monitoring

### Health Checks

- **Application**: http://localhost:3000/health
- **API**: http://localhost:3000/api/health
- **Database**: Check container status

### Logs

```bash
# Application logs
docker-compose logs -f webapp

# Database logs
docker-compose logs -f postgres

# All services
docker-compose logs -f
```

## 🐛 Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. **Database connection issues**
   - Check if PostgreSQL container is running
   - Verify connection parameters in .env

3. **Keycloak authentication fails**
   - Verify realm and client configuration
   - Check redirect URIs match exactly

4. **Nginx proxy errors**
   - Check if backend services are healthy
   - Verify nginx configuration

### Reset Everything

```bash
# Stop and remove all containers, volumes, and networks
docker-compose down -v
docker system prune -f

# Start fresh
docker-compose -f docker-compose.dev.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Resources

- [Keycloak Documentation](https://www.keycloak.org/docs/)
- [Express.js Guide](https://expressjs.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Happy Traveling! 🌍✈️**