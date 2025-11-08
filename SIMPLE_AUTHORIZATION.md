# 🎯 Simple Authorization Guide

## ⚠️ The OAuth2 Form is Confusing - Here's the Simple Way

When you click "Authorize", you see OAuth2 form with username/password fields. **Don't use those!**

---

## ✅ Simple 3-Step Process

### Step 1: Login to Get Token

1. Find `POST /auth/login` endpoint
2. Click "Try it out"
3. Enter:
   - `username`: `demo_user`
   - `password`: `demo123456`
4. Click "Execute"
5. **Copy the `access_token`** (the long string starting with `eyJ...`)

---

### Step 2: Find the "Value" Field

1. Click green **"Authorize"** button (top right)
2. **Scroll down** in the modal window
3. **Look for** a field labeled "Value" (it's below the OAuth2 form)
4. **Paste your token** there

---

### Step 3: Authorize

1. Click "Authorize" button
2. Click "Close"
3. ✅ Done! All endpoints will now work

---

## 🔍 Can't Find "Value" Field?

**Use Manual Method Instead:**

### For Each Request:

1. Click "Try it out" on any endpoint
2. Scroll down to see request details
3. Look for "Authorization" or "Headers" section
4. Add:
   - **Header name**: `Authorization`
   - **Header value**: `Bearer YOUR_ACCESS_TOKEN_HERE`
5. Click "Execute"

---

## 📝 Example: Adding Token Manually

**For `GET /proxy` endpoint:**

1. Click "Try it out"
2. Scroll down
3. Find "Authorization" section
4. Enter:
   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
5. Click "Execute"

---

## 🎯 Quick Reference

**Get Token:**
```bash
POST /auth/login
username: demo_user
password: demo123456
```

**Use Token:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

**Remember: Get token from login endpoint first, then paste it (not username/password)!** ✅


