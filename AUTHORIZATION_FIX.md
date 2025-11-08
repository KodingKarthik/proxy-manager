# 🔐 Authorization Fix - Based on Your Interface

## ⚠️ Problem

The "Authorize" button shows **only** OAuth2 form fields (username/password), but **no "Value" field** to paste your token directly.

**This is normal!** Swagger UI's OAuth2PasswordBearer doesn't always show a simple token input.

---

## ✅ Solution: Skip Authorize Button, Use Manual Headers

Since the OAuth2 form doesn't work for direct token entry, **skip the Authorize button** and manually add the token to each request.

---

## 📋 Step-by-Step Instructions

### Step 1: Login to Get Token

1. **Find** `POST /auth/login` endpoint (under "auth" section)
2. **Click** "Try it out"
3. **Enter** credentials in form fields:
   - `username`: `demo_user`
   - `password`: `demo123456`
4. **Click** "Execute"
5. **Copy the `access_token`** from response:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "refresh_token": "...",
     "token_type": "bearer"
   }
   ```
   **Copy the entire `access_token` value!**

---

### Step 2: Close the Authorize Modal

1. **Click** "Close" button in the Authorize modal
2. **Don't use** the OAuth2 form (it won't work)

---

### Step 3: Use Token in Each Request

**For each endpoint that needs authentication:**

1. **Find** the endpoint (e.g., `GET /proxy` or `POST /proxies`)
2. **Click** "Try it out"
3. **Scroll down** to see the request parameters
4. **Look for** "Authorization" or "Headers" section
5. **Add** the token:
   - **Header name**: `Authorization`
   - **Header value**: `Bearer YOUR_ACCESS_TOKEN_HERE`
     - Replace `YOUR_ACCESS_TOKEN_HERE` with your token from Step 1
     - Example: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
6. **Click** "Execute"

---

## 🎯 Example: Getting a Proxy

**Step 1: Click "Try it out" on `GET /proxy`**

**Step 2: Scroll down to see request parameters**

**Step 3: Find "Authorization" or "Headers" section**

**Step 4: Add header:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Step 5: Click "Execute"**

✅ **Done!** The request will work with authentication.

---

## 📝 Quick Reference

**Token Format:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Important:**
- Include `Bearer ` (with space) before the token
- Use the full token (starts with `eyJ...`)
- Add this header to **every** authenticated request

---

## 🔧 Alternative: Use curl (Easier for Testing)

If Swagger UI is confusing, use curl commands:

### Step 1: Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo_user&password=demo123456"
```

**Copy the `access_token` from response!**

### Step 2: Use Token
```bash
# Replace YOUR_TOKEN with your access_token
curl -X GET "http://localhost:8000/proxy?strategy=health_score" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 Summary

1. ✅ **Login** using `POST /auth/login` → Get `access_token`
2. ✅ **Close** the Authorize modal (don't use OAuth2 form)
3. ✅ **For each request**: Add `Authorization: Bearer TOKEN` header manually
4. ✅ **Click** "Execute"

**The key: Skip the Authorize button and manually add the token header to each request!** ✅


