📋 KEYCLOAK QUICK REFERENCE CARD
================================

🌐 ACCESS URLS:
- Keycloak Admin: http://localhost:8081
- Travel Blog: http://localhost:3000

🔑 ADMIN CREDENTIALS:
- Username: admin
- Password: admin123

⚡ QUICK SETUP (AUTOMATED):
```bash
# Install jq if not available (required for script)
brew install jq  # macOS
# or
sudo apt-get install jq  # Ubuntu

# Run automated configuration
./configure-keycloak.sh
```

📖 MANUAL SETUP STEPS:
1. Go to http://localhost:8081
2. Login with admin/admin123
3. Create realm: "vedablog"
4. Create client: "vedablog-client"
5. Configure redirect URIs
6. Enable user registration
7. Create test users

🎯 CRITICAL SETTINGS:
- Realm Name: vedablog
- Client ID: vedablog-client
- Client Type: OpenID Connect (Public)
- Redirect URIs: http://localhost:3000/*
- User Registration: ENABLED
- Remember Me: ENABLED

👤 TEST USER CREDENTIALS:
- Username: traveler1
- Password: traveler123
- Email: traveler@example.com

🔧 TROUBLESHOOTING:
- If login fails: Check redirect URIs
- If registration disabled: Enable in Login settings
- If session expires: Adjust timeout settings
- If access denied: Verify client configuration

📚 DOCUMENTATION:
- Full Guide: KEYCLOAK_CONFIGURATION_GUIDE.md
- Realm Config: keycloak/realm-config.json
- Auto Script: configure-keycloak.sh

🚀 NEXT STEPS:
1. Configure Keycloak (use script or manual)
2. Test login at http://localhost:3000
3. Register new users
4. Test favorites functionality