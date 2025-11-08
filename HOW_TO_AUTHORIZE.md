# 🔐 How to Authorize in Swagger UI - Step by Step

## ⚠️ Important: Don't Use the OAuth2 Form!

The "Authorize" button shows an OAuth2 form, but **you need to get the token first** using the login endpoint.

---

## ✅ Correct Method: Get Token First, Then Authorize

### Step 1: Login to Get Token

**In Swagger UI (http://localhost:8000/docs):**

1. **Find** `POST /auth/login` endpoint (under "auth" section)
2. **Click** "Try it out"
3. **Enter** credentials in the form fields:
   - `username`: `demo_user`
   - `password`: `demo123456`
4. **Click** "Execute"
5. **Copy the `access_token`** from the response:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vX3VzZXIiLCJ1c2VyX2lkIjoxLCJleHAiOjE3MzEwNzY5MTJ9...",
     "refresh_token": "...",
     "token_type": "bearer"
   }
   ```
   **Copy the entire `access_token` value!**

---

### Step 2: Authorize with Token

**Option A: If You See a "Value" Field (Easiest)**

1. **Click** the green **"Authorize"** button (top right)
2. **Scroll down** in the modal - look for a field labeled:
   - "Value" or
   - "Bearer Token" or
   - "Token" or
   - Just an empty input field
3. **Paste your `access_token`** in that field
   - Paste the entire token (starts with `eyJ...`)
   - **DO NOT** enter username/password
4. **Click** "Authorize"
5. **Click** "Close"

**Option B: If You Only See OAuth2 Form (Skip Authorize Button)**

If the Authorize modal only shows:
- username field
- password field
- client_id field
- client_secret field

**Then skip the Authorize button** and use this method instead:

1. **Close** the Authorize modal
2. For each endpoint that needs authentication:
   - Click "Try it out"
   - Scroll down to see the request
   - Look for "Authorization" or "Headers" section
   - Add manually:
     - Header name: `Authorization`
     - Header value: `Bearer YOUR_ACCESS_TOKEN_HERE`
   - Click "Execute"

---

## 🎯 Visual Guide

### What You Should See:

**After clicking "Authorize" button:**

```
┌─────────────────────────────────────────┐
│ Available authorizations          [X]   │
├─────────────────────────────────────────┤
│ OAuth2PasswordBearer (OAuth2, password) │
│                                         │
│ Token URL: auth/login                   │
│ Flow: password                          │
│                                         │
│ username: [input field]                 │
│ password: [input field]                 │
│                                         │
│ ⬇️ SCROLL DOWN ⬇️                       │
│                                         │
│ Value: [THIS IS WHERE YOU PASTE TOKEN]  │
│                                         │
│ [Authorize] [Close]                     │
└─────────────────────────────────────────┘
```

**Look for the "Value" field below the OAuth2 form!**

---

## 🔧 Alternative: Manual Header Entry

If you can't find the "Value" field, manually add the token to each request:

### For Each Endpoint:

1. **Find** the endpoint (e.g., `GET /proxy`)
2. **Click** "Try it out"
3. **Scroll down** to see request parameters
4. **Look for** "Authorization" or "Headers" section
5. **Add**:
   - **Name**: `Authorization`
   - **Value**: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (your full token)
6. **Click** "Execute"

---

## 📝 Quick Test

### Step 1: Login (Get Token)
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo_user&password=demo123456"
```

**Copy the `access_token` from response!**

### Step 2: Test with Token
```bash
# Replace YOUR_TOKEN with the access_token from Step 1
curl -X GET "http://localhost:8000/proxy?strategy=health_score" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 Summary

1. ✅ **First**: Use `POST /auth/login` endpoint → Get `access_token`
2. ✅ **Then**: Click "Authorize" button
3. ✅ **Find**: "Value" field (scroll down if needed)
4. ✅ **Paste**: Your `access_token` (the long string)
5. ✅ **Click**: "Authorize" → "Close"

**OR** if "Value" field doesn't exist:
- Skip Authorize button
- Manually add `Authorization: Bearer TOKEN` header to each request

---

## 🔍 Troubleshooting

### "I don't see a 'Value' field"
**Solution:** Scroll down in the Authorize modal, or use manual header entry method.

### "The OAuth2 form doesn't work"
**Solution:** That's correct - don't use it! Get token from login endpoint first.

### "Where do I paste the token?"
**Solution:** Look for a field labeled "Value", "Bearer Token", or just an empty input field below the OAuth2 form.

---

**The key: Get token from login endpoint first, then paste it in the "Value" field (not username/password fields)!** ✅


