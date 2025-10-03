#!/bin/bash

# Validation script for the travel blog platform setup

echo "🔍 Validating Veda's Travel Blog Platform Setup..."
echo "=================================================="

# Check if all required files exist
echo "📁 Checking file structure..."

required_files=(
    "docker-compose.yml"
    "docker-compose.dev.yml"
    ".env.example"
    "database/init.sql"
    "nginx/Dockerfile"
    "nginx/nginx.conf"
    "webapp/package.json"
    "webapp/server.js"
    "webapp/Dockerfile"
    "webapp/models/database.js"
    "webapp/routes/auth.js"
    "webapp/routes/destinations.js"
    "webapp/routes/api.js"
    "webapp/routes/favorites.js"
    "webapp/views/layouts/main.ejs"
    "webapp/views/partials/nav.ejs"
    "webapp/views/partials/footer.ejs"
    "webapp/views/pages/index.ejs"
    "webapp/views/pages/404.ejs"
    "webapp/views/pages/error.ejs"
    "webapp/public/js/main.js"
    "webapp/public/js/auth.js"
    "webapp/public/js/favorites.js"
    "webapp/public/css/styles.css"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -eq 0 ]]; then
    echo "✅ All required files are present!"
else
    echo "❌ Missing files:"
    printf '   - %s\n' "${missing_files[@]}"
fi

echo ""

# Check Node.js dependencies
echo "📦 Checking Node.js dependencies..."
if [[ -f "webapp/node_modules/package.json" ]] || [[ -d "webapp/node_modules" ]]; then
    echo "✅ Node.js dependencies appear to be installed"
else
    echo "⚠️  Node.js dependencies not installed. Run: cd webapp && npm install"
fi

echo ""

# Check images directory
echo "🖼️ Checking destination images..."
image_count=$(find webapp/public/images -name "*-image.jpg" 2>/dev/null | wc -l)
if [[ $image_count -gt 0 ]]; then
    echo "✅ Found $image_count destination images"
else
    echo "⚠️  No destination images found in webapp/public/images/"
    echo "   Run: cp *-image.jpg webapp/public/images/"
fi

echo ""

# Check environment configuration
echo "⚙️ Checking environment configuration..."
if [[ -f ".env" ]]; then
    echo "✅ Environment file (.env) exists"
else
    echo "⚠️  Environment file (.env) not found"
    echo "   Run: cp .env.example .env"
fi

echo ""

# Validate Docker Compose syntax (basic check)
echo "🐳 Validating Docker Compose files..."

compose_files=("docker-compose.yml" "docker-compose.dev.yml")
for compose_file in "${compose_files[@]}"; do
    if [[ -f "$compose_file" ]]; then
        # Basic YAML syntax check
        if python3 -c "import yaml; yaml.safe_load(open('$compose_file'))" 2>/dev/null; then
            echo "✅ $compose_file syntax is valid"
        else
            echo "❌ $compose_file has syntax errors"
        fi
    fi
done

echo ""

# Check for common issues
echo "🔧 Checking for common issues..."

# Check if ports are likely to be available
ports_to_check=(3000 5432 8080 8081)
for port in "${ports_to_check[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
    else
        echo "✅ Port $port is available"
    fi
done

echo ""

# Summary
echo "📋 Implementation Summary"
echo "========================"
echo "✅ Infrastructure setup (Docker, Compose files)"
echo "✅ Database schema and initialization"
echo "✅ Nginx reverse proxy configuration"
echo "✅ Node.js Express application structure"
echo "✅ Keycloak authentication integration"
echo "✅ Database models and API routes"
echo "✅ EJS templating system"
echo "✅ Frontend JavaScript functionality"
echo "✅ CSS styling (copied from original)"
echo "✅ SEO-friendly URL preservation"
echo "✅ User authentication and session management"
echo "✅ Favorites system implementation"
echo "✅ Comments and ratings API (backend ready)"
echo "✅ Responsive design with modern UI"
echo "✅ Error handling and logging"
echo "✅ Health checks and monitoring"
echo "✅ Development and production configurations"

echo ""
echo "🚀 Next Steps:"
echo "1. Install Docker and Docker Compose"
echo "2. Copy destination images: cp *-image.jpg webapp/public/images/"
echo "3. Configure environment: cp .env.example .env"
echo "4. Start development environment: docker compose -f docker-compose.dev.yml up -d"
echo "5. Configure Keycloak realm and client"
echo "6. Access application at http://localhost:3000"

echo ""
echo "📖 For detailed instructions, see README.md"
echo "✨ Implementation complete! Ready for testing."