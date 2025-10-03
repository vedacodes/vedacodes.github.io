#!/bin/bash

# Keycloak Troubleshooting Script for Server Deployment

echo "🔍 Keycloak Troubleshooting for Server: 98.84.38.150"
echo "=================================================="

SERVER_IP="98.84.38.150"
KEYCLOAK_PORT="8080"
NGINX_PORT="80"

echo "📋 Checking Docker containers..."
docker compose ps

echo ""
echo "📋 Checking container logs..."
echo "Keycloak logs (last 20 lines):"
docker compose logs --tail=20 keycloak

echo ""
echo "Nginx logs (last 10 lines):"
docker compose logs --tail=10 nginx

echo ""
echo "🌐 Testing network connectivity..."

# Test if ports are open
echo "Testing port $KEYCLOAK_PORT (Keycloak direct):"
if nc -z localhost $KEYCLOAK_PORT 2>/dev/null; then
    echo "✅ Port $KEYCLOAK_PORT is open locally"
else
    echo "❌ Port $KEYCLOAK_PORT is not accessible locally"
fi

echo "Testing port $NGINX_PORT (Nginx):"
if nc -z localhost $NGINX_PORT 2>/dev/null; then
    echo "✅ Port $NGINX_PORT is open locally"
else
    echo "❌ Port $NGINX_PORT is not accessible locally"
fi

echo ""
echo "🔥 Firewall check (common ports that should be open):"
echo "Port 80 (HTTP): Should be open for web access"
echo "Port 8080 (Keycloak): Should be open for admin access"
echo "Port 443 (HTTPS): Should be open for secure web access"
echo "Port 22 (SSH): Should be open for server management"

echo ""
echo "🌍 Access URLs you should try:"
echo "1. Keycloak Admin (Direct): http://$SERVER_IP:$KEYCLOAK_PORT"
echo "2. Keycloak Admin (via Nginx): http://$SERVER_IP/auth/"
echo "3. Web Application: http://$SERVER_IP"
echo "4. Health Check: http://$SERVER_IP/health"

echo ""
echo "🔧 Common solutions:"
echo ""
echo "Solution 1: Restart containers with exposed ports"
echo "docker compose down"
echo "docker compose up -d"
echo ""
echo "Solution 2: Check if Keycloak is ready (it takes 2-3 minutes to start)"
echo "docker compose logs -f keycloak"
echo ""
echo "Solution 3: Configure firewall (if running on cloud provider)"
echo "# For Ubuntu/Debian:"
echo "sudo ufw allow 80"
echo "sudo ufw allow 8080"
echo "sudo ufw allow 443"
echo ""
echo "# For CentOS/RHEL:"
echo "sudo firewall-cmd --permanent --add-port=80/tcp"
echo "sudo firewall-cmd --permanent --add-port=8080/tcp"
echo "sudo firewall-cmd --permanent --add-port=443/tcp"
echo "sudo firewall-cmd --reload"
echo ""
echo "Solution 4: Check cloud provider security groups"
echo "Make sure your cloud provider (AWS, GCP, Azure, etc.) allows inbound traffic on ports 80 and 8080"

echo ""
echo "🚨 If still not working, run these diagnostic commands:"
echo "docker compose ps"
echo "docker compose logs keycloak"
echo "docker compose logs nginx"
echo "netstat -tlnp | grep -E ':(80|8080)'"

echo ""
echo "💡 Quick test commands:"
echo "curl -I http://localhost:80"
echo "curl -I http://localhost:8080"
echo "curl -I http://$SERVER_IP:80"
echo "curl -I http://$SERVER_IP:8080"