# 🔧 Quick Fix: 401 Unauthorized Error

## ⚠️ Problem

Getting `401 Unauthorized` error when accessing `/proxies` endpoint.

**Error:**
```json
{
  "detail": "Not authenticated"
}
```

---

## ✅ Solution: Add Authorization Header

You need to add your `access_token` to the request.

---

## 📋 Step-by-Step Fix

### Step 1: Get Your Token (If You Don't Have It)

**Login first:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo_user&password=demo123456"
```

**Copy the `access_token` from the response!**

---

### Step 2: Add Token to Your Request

**Your current command (missing token):**
```bash
curl -X 'GET' \
  'http://localhost:8000/proxies?working_only=false&limit=100&offset=0' \
  -H 'accept: application/json'
```

**✅ Fixed command (with token):**
```bash
curl -X 'GET' \
  'http://localhost:8000/proxies?working_only=false&limit=100&offset=0' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN_HERE'
```

**Replace `YOUR_ACCESS_TOKEN_HERE` with your actual token!**

---

## 🎯 Complete Example

### Step 1: Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo_user&password=demo123456"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

**Copy the `access_token`!**

### Step 2: Use Token
```bash
# Replace YOUR_TOKEN with the access_token from Step 1
curl -X 'GET' \
  'http://localhost:8000/proxies?working_only=false&limit=100&offset=0' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**✅ This will work!**

---

## 🔧 In Swagger UI

**If using Swagger UI:**

1. **Click** "Try it out" on `GET /proxies`
2. **Scroll down** to see request parameters
3. **Find** "Authorization" or "Headers" section
4. **Add**:
   - **Header name**: `Authorization`
   - **Header value**: `Bearer YOUR_ACCESS_TOKEN_HERE`
5. **Click** "Execute"

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

## 🎯 Summary

**The fix:**
```bash
-H 'Authorization: Bearer YOUR_ACCESS_TOKEN_HERE'
```

**Add this header to your curl command!** ✅


