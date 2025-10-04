#!/bin/bash

# Automated Keycloak Configuration Script for Veda's Travel Diary

echo "🔐 Configuring Keycloak for Veda's Travel Diary..."
echo "================================================="

KEYCLOAK_URL="http://localhost:8081"
REALM_NAME="vedablog"
CLIENT_ID="vedablog-client"
ADMIN_USER="admin"
ADMIN_PASS="admin123"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if Keycloak is ready
check_keycloak() {
    echo -e "${BLUE}Checking if Keycloak is ready...${NC}"
    for i in {1..30}; do
        if curl -s "$KEYCLOAK_URL" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Keycloak is ready!${NC}"
            return 0
        fi
        echo -e "${YELLOW}Waiting for Keycloak... ($i/30)${NC}"
        sleep 2
    done
    echo -e "${RED}❌ Keycloak is not responding. Please check if it's running.${NC}"
    exit 1
}

# Function to get admin token
get_admin_token() {
    echo -e "${BLUE}Getting admin access token...${NC}"
    TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASS" \
        -d "grant_type=password" \
        -d "client_id=admin-cli" | jq -r '.access_token')
    
    if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
        echo -e "${RED}❌ Failed to get admin token. Please check credentials.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Admin token obtained${NC}"
}

# Function to check if realm exists
check_realm_exists() {
    echo -e "${BLUE}Checking if realm '$REALM_NAME' exists...${NC}"
    REALM_EXISTS=$(curl -s -H "Authorization: Bearer $TOKEN" \
        "$KEYCLOAK_URL/admin/realms/$REALM_NAME" | jq -r '.realm')
    
    if [ "$REALM_EXISTS" = "$REALM_NAME" ]; then
        echo -e "${YELLOW}⚠️  Realm '$REALM_NAME' already exists${NC}"
        return 0
    else
        echo -e "${BLUE}Realm '$REALM_NAME' does not exist, will create it${NC}"
        return 1
    fi
}

# Function to create realm
create_realm() {
    echo -e "${BLUE}Creating realm '$REALM_NAME'...${NC}"
    
    REALM_CONFIG='{
        "realm": "'$REALM_NAME'",
        "enabled": true,
        "displayName": "Vedas Travel Diary",
        "displayNameHtml": "<span>Vedas <strong>Travel Diary</strong></span>",
        "registrationAllowed": true,
        "registrationEmailAsUsername": false,
        "editUsernameAllowed": true,
        "resetPasswordAllowed": true,
        "rememberMe": true,
        "verifyEmail": false,
        "loginWithEmailAllowed": true,
        "duplicateEmailsAllowed": false,
        "bruteForceProtected": true,
        "permanentLockout": false,
        "maxFailureWaitSeconds": 900,
        "minimumQuickLoginWaitSeconds": 60,
        "waitIncrementSeconds": 60,
        "quickLoginCheckMilliSeconds": 1000,
        "maxDeltaTimeSeconds": 43200,
        "failureFactor": 5
    }'
    
    RESPONSE=$(curl -s -w "%{http_code}" -X POST "$KEYCLOAK_URL/admin/realms" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$REALM_CONFIG")
    
    HTTP_CODE="${RESPONSE: -3}"
    if [ "$HTTP_CODE" = "201" ]; then
        echo -e "${GREEN}✅ Realm created successfully${NC}"
    else
        echo -e "${RED}❌ Failed to create realm. HTTP Code: $HTTP_CODE${NC}"
        exit 1
    fi
}

# Function to create client
create_client() {
    echo -e "${BLUE}Creating client '$CLIENT_ID'...${NC}"
    
    CLIENT_CONFIG='{
        "clientId": "'$CLIENT_ID'",
        "name": "Vedas Travel Blog Web App",
        "description": "Main web application for the travel blog",
        "rootUrl": "http://localhost:3000",
        "baseUrl": "/",
        "enabled": true,
        "publicClient": true,
        "standardFlowEnabled": true,
        "implicitFlowEnabled": false,
        "directAccessGrantsEnabled": true,
        "serviceAccountsEnabled": false,
        "frontchannelLogout": false,
        "protocol": "openid-connect",
        "redirectUris": [
            "http://localhost:3000/*",
            "http://localhost:3000/auth/*",
            "http://localhost:3000/auth/callback"
        ],
        "webOrigins": [
            "http://localhost:3000"
        ],
        "attributes": {
            "post.logout.redirect.uris": "http://localhost:3000/*"
        },
        "defaultClientScopes": [
            "web-origins",
            "acr",
            "profile",
            "roles",
            "email"
        ]
    }'
    
    RESPONSE=$(curl -s -w "%{http_code}" -X POST "$KEYCLOAK_URL/admin/realms/$REALM_NAME/clients" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$CLIENT_CONFIG")
    
    HTTP_CODE="${RESPONSE: -3}"
    if [ "$HTTP_CODE" = "201" ]; then
        echo -e "${GREEN}✅ Client created successfully${NC}"
    else
        echo -e "${RED}❌ Failed to create client. HTTP Code: $HTTP_CODE${NC}"
        exit 1
    fi
}

# Function to create test user
create_test_user() {
    echo -e "${BLUE}Creating test user 'traveler1'...${NC}"
    
    USER_CONFIG='{
        "username": "traveler1",
        "enabled": true,
        "emailVerified": true,
        "firstName": "John",
        "lastName": "Traveler",
        "email": "traveler@example.com",
        "attributes": {
            "displayName": ["John the Traveler"],
            "bio": ["Love exploring new destinations and cultures!"]
        }
    }'
    
    # Create user
    RESPONSE=$(curl -s -w "%{http_code}" -X POST "$KEYCLOAK_URL/admin/realms/$REALM_NAME/users" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$USER_CONFIG")
    
    HTTP_CODE="${RESPONSE: -3}"
    if [ "$HTTP_CODE" = "201" ]; then
        echo -e "${GREEN}✅ Test user created successfully${NC}"
        
        # Get user ID
        USER_ID=$(curl -s -H "Authorization: Bearer $TOKEN" \
            "$KEYCLOAK_URL/admin/realms/$REALM_NAME/users?username=traveler1" | jq -r '.[0].id')
        
        # Set password
        PASSWORD_CONFIG='{
            "type": "password",
            "value": "traveler123",
            "temporary": false
        }'
        
        curl -s -X PUT "$KEYCLOAK_URL/admin/realms/$REALM_NAME/users/$USER_ID/reset-password" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$PASSWORD_CONFIG"
        
        echo -e "${GREEN}✅ Test user password set${NC}"
    else
        echo -e "${YELLOW}⚠️  Test user might already exist or failed to create${NC}"
    fi
}

# Function to display configuration summary
display_summary() {
    echo ""
    echo -e "${GREEN}🎉 Keycloak Configuration Complete!${NC}"
    echo "=================================="
    echo ""
    echo -e "${BLUE}📋 Configuration Summary:${NC}"
    echo "• Keycloak URL: $KEYCLOAK_URL"
    echo "• Realm: $REALM_NAME"
    echo "• Client ID: $CLIENT_ID"
    echo "• User Registration: Enabled"
    echo "• Remember Me: Enabled"
    echo "• Brute Force Protection: Enabled"
    echo ""
    echo -e "${BLUE}🔑 Admin Access:${NC}"
    echo "• URL: $KEYCLOAK_URL/admin/"
    echo "• Username: $ADMIN_USER"
    echo "• Password: $ADMIN_PASS"
    echo ""
    echo -e "${BLUE}👤 Test User Credentials:${NC}"
    echo "• Username: traveler1"
    echo "• Password: traveler123"
    echo "• Email: traveler@example.com"
    echo ""
    echo -e "${BLUE}🌐 Next Steps:${NC}"
    echo "1. Visit http://localhost:3000"
    echo "2. Click 'Login' to test authentication"
    echo "3. Try registering a new user"
    echo "4. Test the favorites functionality"
    echo ""
    echo -e "${GREEN}✨ Your travel blog is ready for users!${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}Starting Keycloak configuration...${NC}"
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}❌ jq is required but not installed. Please install jq first.${NC}"
        echo "macOS: brew install jq"
        echo "Ubuntu: sudo apt-get install jq"
        exit 1
    fi
    
    check_keycloak
    get_admin_token
    
    if check_realm_exists; then
        echo -e "${YELLOW}⚠️  Realm already exists, skipping realm creation${NC}"
    else
        create_realm
        sleep 2  # Wait for realm to be fully created
        get_admin_token  # Refresh token for new realm operations
    fi
    
    create_client
    create_test_user
    display_summary
}

# Run main function
main