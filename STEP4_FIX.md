# 🔧 Fix for Step 4 - Login & Authorization

## ⚠️ Problem

Getting "Unprocessable Content" error when trying to use the "Authorize" button in Swagger UI.

## ✅ Solution

The "Authorize" button uses OAuth2 flow, but our login endpoint expects **form data**. Here's the correct way:

---

## 📋 Correct Steps for Step 4

### Method 1: Use Login Endpoint Directly (Recommended)

**Step 4a: Login via POST /auth/login**

1. **Find** `POST /auth/login` endpoint (under "auth" section)
2. **Click** "Try it out"
3. **IMPORTANT:** Use **form data**, not JSON!
   - You should see form fields like:
     ```
     username: [input field]
     password: [input field]
     ```
   - If you see a JSON editor, look for a dropdown to switch to "form" mode
4. **Enter**:
   - `username`: `demo_user`
   - `password`: `demo123456`
5. **Click** "Execute"
6. **Copy the `access_token`** from response:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "refresh_token": "...",
     "token_type": "bearer"
   }
   ```

**Step 4b: Authorize in Swagger UI**

**Option A: Simple Token Authorization (Easiest)**

1. **Click** the green **"Authorize"** button (top right)
2. **Look for** a field that says "Value" or "Bearer Token"
3. **Paste ONLY your `access_token`** (the long string, e.g., `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)
4. **DO NOT** enter username/password
5. **Click** "Authorize"
6. **Click** "Close"

**Option B: Manual Token Entry (If Authorize doesn't work)**

1. **Skip the Authorize button**
2. For each endpoint that needs authentication:
   - Click "Try it out"
   - Look for "Authorization" or "Headers" section
   - Add header:
     - Name: `Authorization`
     - Value: `Bearer YOUR_ACCESS_TOKEN_HERE`
   - Then click "Execute"

---

## 🎯 Quick Fix - Use curl Instead

If Swagger UI is confusing, use curl:

### Step 1: Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo_user&password=demo123456"
```

**Copy the `access_token` from the response!**

### Step 2: Use Token in Requests
```bash
# Replace YOUR_TOKEN with the access_token from Step 1
curl -X GET "http://localhost:8000/proxy?strategy=health_score" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔍 Troubleshooting

### Issue: "Unprocessable Content" in Authorize button
**Solution:** Don't use the OAuth2 form in the Authorize button. Instead:
- Use the login endpoint first (`POST /auth/login`)
- Get the token
- Paste just the token in the "Value" field

### Issue: Login endpoint shows JSON editor instead of form
**Solution:** 
- Look for a dropdown or button to switch to "form" mode
- Or use curl command instead

### Issue: Can't find where to paste token
**Solution:**
- Skip the Authorize button
- Manually add `Authorization: Bearer TOKEN` header to each request

---

## ✅ Correct Flow Summary

1. ✅ Register user (`POST /auth/register`)
2. ✅ Login (`POST /auth/login`) - Use **form data**
3. ✅ Copy `access_token` from response
4. ✅ Authorize:
   - Click "Authorize" button
   - Paste **ONLY the token** (not username/password)
   - OR manually add `Authorization: Bearer TOKEN` header

---

## 📝 Example: Manual Token Entry

If the Authorize button doesn't work, manually add the token:

1. **Find** `GET /proxy` endpoint
2. **Click** "Try it out"
3. **Scroll down** to see request details
4. **Look for** "Authorization" or "Headers" section
5. **Add**:
   - Header name: `Authorization`
   - Header value: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (your token)
6. **Click** "Execute"

---

**The key is: Use the login endpoint first, then paste the token (not username/password) in the Authorize button!** ✅

