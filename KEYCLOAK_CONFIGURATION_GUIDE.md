# 🔐 Keycloak Configuration Guide for Veda's Travel Diary

## Overview
This guide will walk you through configuring Keycloak for user authentication in your travel blog platform. Keycloak will handle user registration, login, logout, and session management.

## Prerequisites
- Keycloak running at http://localhost:8081
- Admin credentials: admin/admin123
- Web application running at http://localhost:3000

---

## Step 1: Access Keycloak Admin Console

1. **Open your browser** and navigate to: http://localhost:8081
2. **Click "Administration Console"**
3. **Login with:**
   - Username: `admin`
   - Password: `admin123`

You should now see the Keycloak admin dashboard.

---

## Step 2: Create a New Realm

A realm is like a tenant in Keycloak - it isolates users and applications.

### 2.1 Create Realm
1. **Click the dropdown** next to "Master" in the top-left corner
2. **Click "Create Realm"**
3. **Fill in the details:**
   - **Realm name**: `vedablog`
   - **Enabled**: ✅ (checked)
4. **Click "Create"**

### 2.2 Configure Realm Settings
1. **Go to Realm Settings** (left sidebar)
2. **General tab:**
   - **Display name**: `Veda's Travel Diary`
   - **HTML Display name**: `<span>Veda's <strong>Travel Diary</strong></span>`
   - **Frontend URL**: `http://localhost:8081` (for development)
3. **Login tab:**
   - **User registration**: ✅ Enable (allows new users to register)
   - **Edit username**: ✅ Enable
   - **Forgot password**: ✅ Enable
   - **Remember me**: ✅ Enable
   - **Verify email**: ❌ Disable (for development)
   - **Login with email**: ✅ Enable
4. **Email tab:**
   - Skip for now (email will work without SMTP in development)
5. **Themes tab:**
   - **Login theme**: `keycloak` (default)
   - **Account theme**: `keycloak`
6. **Click "Save"**

---

## Step 3: Create a Client Application

A client represents your web application in Keycloak.

### 3.1 Create Client
1. **Go to Clients** (left sidebar)
2. **Click "Create client"**
3. **General Settings:**
   - **Client type**: `OpenID Connect`
   - **Client ID**: `vedablog-client`
   - **Name**: `Veda's Travel Blog Web App`
   - **Description**: `Main web application for the travel blog`
   - **Always display in console**: ❌ (unchecked)
4. **Click "Next"**

### 3.2 Capability Config
1. **Client authentication**: ❌ OFF (public client)
2. **Authorization**: ❌ OFF
3. **Authentication flow:**
   - **Standard flow**: ✅ Enable (OAuth 2.0 Authorization Code Flow)
   - **Direct access grants**: ✅ Enable (for API access)
   - **Implicit flow**: ❌ Disable
   - **Service accounts roles**: ❌ Disable
   - **OAuth 2.0 Device Authorization Grant**: ❌ Disable
   - **OIDC CIBA Grant**: ❌ Disable
4. **Click "Next"**

### 3.3 Login Settings
1. **Root URL**: `http://localhost:3000`
2. **Home URL**: `http://localhost:3000`
3. **Valid redirect URIs**: 
   ```
   http://localhost:3000/*
   http://localhost:3000/auth/*
   http://localhost:3000/auth/callback
   ```
4. **Valid post logout redirect URIs**: 
   ```
   http://localhost:3000/*
   http://localhost:3000
   ```
5. **Web origins**: `http://localhost:3000`
6. **Click "Save"**

### 3.4 Advanced Client Settings
1. **Go to your client** → **Settings tab**
2. **Advanced Settings:**
   - **Access Token Lifespan**: `15 minutes` (default)
   - **Client Session Idle**: `30 minutes`
   - **Client Session Max**: `12 hours`
3. **Login Settings:**
   - **Login theme**: Leave empty (inherit from realm)
4. **Click "Save"**

---

## Step 4: Configure Client Scopes

Client scopes define what information your application can access.

### 4.1 Check Default Scopes
1. **Go to your client** → **Client scopes tab**
2. **Default client scopes** should include:
   - `web-origins`
   - `acr`
   - `profile`
   - `roles`
   - `email`

These are automatically assigned and provide basic user information.

---

## Step 5: Configure User Attributes

Set up additional user profile attributes for the travel blog.

### 5.1 Create User Attributes
1. **Go to Realm Settings** → **User Profile tab**
2. **Click "Create attribute"** and add these attributes:

**Attribute 1: Display Name**
- **Name**: `displayName`
- **Display name**: `Display Name`
- **Required**: ❌
- **Permissions**: User can view and edit
- **Annotations**: None

**Attribute 2: Bio**
- **Name**: `bio`
- **Display name**: `Travel Bio`
- **Required**: ❌
- **Permissions**: User can view and edit
- **Annotations**: None

**Attribute 3: Favorite Destinations Count**
- **Name**: `favoritesCount`
- **Display name**: `Favorites Count`
- **Required**: ❌
- **Permissions**: Admin only
- **Annotations**: None

3. **Click "Save"** for each attribute

---

## Step 6: Create Test Users

Create some test users to verify the setup.

### 6.1 Create Admin User
1. **Go to Users** (left sidebar)
2. **Click "Create new user"**
3. **User details:**
   - **Username**: `admin`
   - **Email**: `admin@vedacodes.com`
   - **First name**: `Admin`
   - **Last name**: `User`
   - **Enabled**: ✅
4. **Click "Create"**
5. **Go to Credentials tab**
6. **Click "Set password"**
7. **Set password**: `admin123`
8. **Temporary**: ❌ (permanent password)
9. **Click "Save"**

### 6.2 Create Test User
1. **Create another user:**
   - **Username**: `traveler1`
   - **Email**: `traveler@example.com`
   - **First name**: `John`
   - **Last name**: `Traveler`
   - **Enabled**: ✅
2. **Set password**: `traveler123` (permanent)

---

## Step 7: Configure Themes (Optional)

Customize the login page to match your travel blog theme.

### 7.1 Basic Theme Customization
1. **Go to Realm Settings** → **Themes tab**
2. **Login theme**: `keycloak`
3. **Account theme**: `keycloak`
4. **Email theme**: `keycloak`
5. **Admin console theme**: `keycloak`

For custom themes, you would need to create custom theme files in the Keycloak installation.

---

## Step 8: Configure Session Settings

Set up session management for optimal user experience.

### 8.1 Session Settings
1. **Go to Realm Settings** → **Sessions tab**
2. **Configure timeouts:**
   - **SSO Session Idle**: `30 minutes`
   - **SSO Session Max**: `12 hours`
   - **SSO Session Idle Remember Me**: `2 days`
   - **SSO Session Max Remember Me**: `30 days`
   - **Client Session Idle**: `30 minutes`
   - **Client Session Max**: `12 hours`
   - **Offline Session Idle**: `30 days`
   - **Offline Session Max Limited**: ✅ Enable
   - **Offline Session Max**: `60 days`
3. **Click "Save"**

---

## Step 9: Configure Security Defenses

Enable security features to protect against common attacks.

### 9.1 Security Defenses
1. **Go to Realm Settings** → **Security Defenses tab**
2. **Headers:**
   - **X-Frame-Options**: `SAMEORIGIN`
   - **Content Security Policy**: `frame-src 'self'; frame-ancestors 'self'; object-src 'none';`
   - **Content Security Policy Report Only**: Leave empty
   - **X-Content-Type-Options**: `nosniff`
   - **X-Robots-Tag**: `none`
   - **X-XSS-Protection**: `1; mode=block`
   - **Strict-Transport-Security**: `max-age=31536000; includeSubDomains` (for HTTPS)
3. **Brute Force Detection:**
   - **Enabled**: ✅
   - **Max Login Failures**: `5`
   - **Wait Increment**: `60 seconds`
   - **Quick Login Check**: `1000 milliseconds`
   - **Minimum Quick Login Wait**: `60 seconds`
   - **Max Wait**: `900 seconds`
   - **Failure Reset Time**: `720 seconds`
4. **Click "Save"**

---

## Step 10: Test the Configuration

### 10.1 Test User Registration
1. **Open**: http://localhost:3000
2. **Click "Login"** (should redirect to Keycloak)
3. **Click "Register"** on the Keycloak login page
4. **Fill out registration form:**
   - Username: `testuser`
   - Email: `test@example.com`
   - First Name: `Test`
   - Last Name: `User`
   - Password: `testpass123`
   - Confirm Password: `testpass123`
5. **Click "Register"**

### 10.2 Test Login Flow
1. **Login with the new user**
2. **Verify redirection** back to your travel blog
3. **Check that user info** is displayed in the navigation
4. **Test logout** functionality

---

## Step 11: Production Configuration

For production deployment, update these settings:

### 11.1 Update URLs for Production
1. **Client Settings:**
   - **Root URL**: `https://yourdomain.com`
   - **Valid redirect URIs**: `https://yourdomain.com/*`
   - **Valid post logout redirect URIs**: `https://yourdomain.com/*`
   - **Web origins**: `https://yourdomain.com`

### 11.2 Security Enhancements
1. **Enable HTTPS requirements**
2. **Configure proper SMTP** for email verification
3. **Enable email verification** for new users
4. **Set stronger password policies**
5. **Configure backup admin users**

---

## Configuration Summary

After completing these steps, you will have:

✅ **Keycloak realm** configured for your travel blog  
✅ **Client application** set up with proper OAuth2/OIDC flows  
✅ **User registration** enabled for new travelers  
✅ **Session management** configured for good UX  
✅ **Security defenses** enabled against attacks  
✅ **Test users** created for validation  
✅ **Integration** with your Node.js application  

## Troubleshooting

### Common Issues:

1. **"Invalid redirect URI"**
   - Check that redirect URIs exactly match your app URLs
   - Ensure no trailing slashes where not expected

2. **Users can't register**
   - Verify "User registration" is enabled in Login settings
   - Check that email requirements match your setup

3. **Login redirect fails**
   - Verify client configuration matches your app's Keycloak settings
   - Check that the client is enabled

4. **Session expires too quickly**
   - Adjust session timeout settings in Sessions tab
   - Enable "Remember Me" for longer sessions

## Next Steps

After configuration:
1. **Test all authentication flows**
2. **Verify user profile management**
3. **Test favorites functionality**
4. **Check logout behavior**
5. **Validate session management**

Your Keycloak instance is now ready to handle user authentication for your travel blog! 🚀