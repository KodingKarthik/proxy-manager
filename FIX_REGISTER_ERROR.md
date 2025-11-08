# Fix for /auth/register 500 Error

## Problem
Getting 500 Internal Server Error when trying to register a user via `/auth/register` endpoint.

## Solution Applied

### Issue
The database tables might not be properly initialized, or models aren't imported before table creation.

### Fix
Updated `database.py` to import all models before creating tables:

```python
# Import all models to ensure they're registered with SQLModel
from .models import User, Proxy, ActivityLog, Blacklist  # noqa: F401
```

## Steps to Fix

### 1. Restart the Server
```bash
# Stop the current server (Ctrl+C)
# Then restart:
./run_server.sh
```

### 2. Test Registration Again
In Swagger UI (http://localhost:8000/docs):
1. Find `POST /auth/register`
2. Click "Try it out"
3. Enter:
   ```json
   {
     "username": "johndoe",
     "email": "john@example.com",
     "password": "securepassword123"
   }
   ```
4. Click "Execute"

### 3. Expected Response
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2024-..."
}
```

## Alternative: Manual Database Reset

If the issue persists, you can reset the database:

```bash
# Stop server
# Delete database
rm proxy_manager.db

# Restart server (will create new database)
./run_server.sh
```

## Verification

After restarting, check:
1. Server logs show "Database tables initialized"
2. Database file exists: `ls -la proxy_manager.db`
3. Registration works in Swagger UI

---

**The fix has been applied. Restart your server and try again!** ✅

