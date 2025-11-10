# 🔐 Google OAuth Setup Guide - Production Ready

This guide will help you set up real Google OAuth authentication for your application.

## 📋 Prerequisites

1. Google Account
2. Access to Google Cloud Console
3. Your application running on a known domain/localhost

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project" or select existing project
3. Name your project (e.g., "Arabic Legal AI")
4. Note your Project ID

### Step 2: Enable Google+ API

1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google+ API" 
3. Click and "Enable" it
4. Also enable "Google Identity" API

### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" for most applications
3. Fill required fields:
   - **App name**: Arabic Legal AI Assistant
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Add authorized domains if using custom domain
5. Save and continue

### Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Configure:
   - **Name**: Arabic Legal AI Web Client
   - **Authorized JavaScript origins**:
     - `http://localhost:3000` (for development)
     - `https://yourdomain.com` (for production)
   - **Authorized redirect URIs**:
     - `http://localhost:3000` (for development)
     - `https://yourdomain.com` (for production)

### Step 5: Get Your Credentials

1. After creating, you'll see:
   - **Client ID**: `123456789-abc123def456.apps.googleusercontent.com`
   - **Client Secret**: `GOCSPX-1234567890abcdef`
2. **Copy these values** - you'll need them next

## ⚙️ Configure Your Application

### Backend Configuration

Edit `/backend/.env`:

```bash
# Replace with your actual credentials
GOOGLE_CLIENT_ID=123456789-abc123def456.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-1234567890abcdef
```

### Frontend Configuration

Edit `/frontend/.env`:

```bash
# Replace with your actual Client ID (same as backend)
VITE_GOOGLE_CLIENT_ID=123456789-abc123def456.apps.googleusercontent.com
```

## 🧪 Testing Your Setup

### 1. Restart Your Services

```bash
# Backend
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend  
cd frontend
npm run dev
```

### 2. Test the Configuration

Visit: `http://localhost:8000/api/auth/google/test-info`

Should return:
```json
{
  "environment": "development",
  "google_client_id_configured": true,
  "google_auth_available": true,
  "requires_real_google_token": true
}
```

### 3. Test Frontend Integration

1. Open `http://localhost:3000`
2. Click "Sign in with Google"
3. Google's popup should appear
4. Complete authentication flow
5. User should be logged in

## 🚨 Security Notes

### For Development
- Use `http://localhost:3000` in authorized origins
- Test with your real Google account

### For Production
- **ALWAYS use HTTPS** (`https://yourdomain.com`)
- Add your production domain to authorized origins
- Keep client secrets secure (backend only)
- Consider using environment-specific credentials

## 🔍 Troubleshooting

### Common Issues

1. **"redirect_uri_mismatch"**
   - Check authorized redirect URIs in Google Console
   - Ensure exact match (including http/https, port)

2. **"invalid_client"**
   - Verify Client ID is correct
   - Check if APIs are enabled

3. **CORS errors**
   - Add your domain to authorized JavaScript origins
   - Check backend CORS configuration

4. **"access_blocked"**
   - Complete OAuth consent screen setup
   - Add test users if app is not published

### Debug Commands

```bash
# Check backend configuration
curl http://localhost:8000/api/auth/google/status

# Check if environment variables are loaded
echo $GOOGLE_CLIENT_ID  # (backend)
```

## 📝 Important Notes

1. **Client ID vs Client Secret**:
   - Client ID: Used in frontend (public)
   - Client Secret: Used in backend only (private)

2. **Domain Verification**:
   - For production, verify domain ownership in Google Console

3. **Quota Limits**:
   - Google has rate limits on OAuth requests
   - Monitor usage in Google Console

4. **Publishing Your App**:
   - For production, submit app for verification
   - Until verified, limited to 100 test users

## ✅ Success Criteria

When properly configured, users should be able to:
- Click "Sign in with Google" button
- See Google's authentication popup
- Grant permissions to your app
- Be redirected back and logged in
- Access protected features

Your Google OAuth integration is now production-ready! 🎉