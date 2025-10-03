#!/bin/bash

# Quick Server Setup Script for Keycloak Access

echo "🚀 Setting up Keycloak access on server 98.84.38.150"
echo "=================================================="

# Step 1: Stop current containers
echo "1. Stopping current containers..."
docker compose down

# Step 2: Update environment variables for production
echo "2. Updating environment variables..."
cat > .env << EOF
# Production environment variables for server 98.84.38.150
DB_PASSWORD=vedablog_prod_$(date +%s)
POSTGRES_PASSWORD=postgres_prod_$(date +%s)
KEYCLOAK_ADMIN_PASSWORD=admin_$(date +%s)
KEYCLOAK_DB_PASSWORD=keycloak_prod_$(date +%s)
SESSION_SECRET=$(openssl rand -base64 32)
EOF

echo "✅ Environment variables updated"

# Step 3: Start containers with updated configuration
echo "3. Starting containers..."
docker compose up -d

echo "4. Waiting for services to start (this takes 2-3 minutes)..."
sleep 30

# Step 4: Check status
echo "5. Checking container status..."
docker compose ps

echo ""
echo "🌍 Access URLs:"
echo "- Keycloak Admin Console: http://98.84.38.150:8080"
echo "- Web Application: http://98.84.38.150"
echo "- Keycloak via Nginx: http://98.84.38.150/auth/"

echo ""
echo "🔑 Keycloak Admin Credentials:"
echo "Username: admin"
echo "Password: Check the KEYCLOAK_ADMIN_PASSWORD in .env file"

echo ""
echo "🔧 If still not accessible, check:"
echo "1. Firewall settings (ports 80, 8080, 443 should be open)"
echo "2. Cloud provider security groups"
echo "3. Container logs: docker compose logs keycloak"

echo ""
echo "📋 Firewall commands (run as root):"
echo "# Ubuntu/Debian:"
echo "ufw allow 80 && ufw allow 8080 && ufw allow 443"
echo ""
echo "# CentOS/RHEL:"
echo "firewall-cmd --permanent --add-port=80/tcp"
echo "firewall-cmd --permanent --add-port=8080/tcp"
echo "firewall-cmd --permanent --add-port=443/tcp"
echo "firewall-cmd --reload"

echo ""
echo "🏁 Setup complete! Wait 2-3 minutes for Keycloak to fully start."