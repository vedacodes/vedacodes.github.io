#!/bin/bash

# Fix Keycloak authentication issue by updating configuration

echo "🔧 Fixing Keycloak authentication configuration..."
echo "================================================="

# Update the Keycloak client configuration with correct URLs
echo "1. Updating Keycloak client configuration..."

# Get admin token
ADMIN_TOKEN=$(curl -s -X POST "http://localhost:8081/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin" \
    -d "password=admin123" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | jq -r '.access_token')

if [ "$ADMIN_TOKEN" = "null" ] || [ -z "$ADMIN_TOKEN" ]; then
    echo "❌ Failed to get admin token"
    exit 1
fi

# Get client ID
CLIENT_ID=$(curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
    "http://localhost:8081/admin/realms/vedablog/clients?clientId=vedablog-client" | jq -r '.[0].id')

if [ "$CLIENT_ID" = "null" ] || [ -z "$CLIENT_ID" ]; then
    echo "❌ Client not found"
    exit 1
fi

# Update client configuration
CLIENT_UPDATE='{
    "redirectUris": [
        "http://localhost:3000/*",
        "http://localhost:3000/auth/*",
        "http://localhost:3000/auth/callback",
        "http://localhost:8080/*",
        "http://localhost:8080/auth/*"
    ],
    "webOrigins": [
        "http://localhost:3000",
        "http://localhost:8080"
    ],
    "attributes": {
        "post.logout.redirect.uris": "http://localhost:3000/* http://localhost:8080/*"
    }
}'

RESPONSE=$(curl -s -w "%{http_code}" -X PUT \
    "http://localhost:8081/admin/realms/vedablog/clients/$CLIENT_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$CLIENT_UPDATE")

HTTP_CODE="${RESPONSE: -3}"
if [ "$HTTP_CODE" = "204" ]; then
    echo "✅ Client configuration updated successfully"
else
    echo "❌ Failed to update client configuration. HTTP Code: $HTTP_CODE"
fi

echo ""
echo "2. Restarting webapp container..."
cd /Users/muralikrishnaarkatavemula/Documents/github/vedacodes.github.io
docker compose -f docker-compose.dev.yml restart webapp

echo ""
echo "3. Waiting for services to restart..."
sleep 10

echo ""
echo "✅ Configuration fix complete!"
echo ""
echo "🧪 Test the fix:"
echo "1. Go to: http://localhost:3000"
echo "2. Click 'Login'"
echo "3. Login with: traveler1 / traveler123"
echo "4. Should redirect back successfully"
echo ""
echo "🔗 Alternative access:"
echo "- Direct app: http://localhost:3000"
echo "- Via nginx: http://localhost:8080"
echo ""
echo "If still having issues, check logs:"
echo "docker compose -f docker-compose.dev.yml logs webapp"