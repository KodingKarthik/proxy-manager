# How to Connect/Add Proxies Through the Website

## Step 1: Start the Server

```bash
./run_server.sh
```

Then open: **http://localhost:8000/docs**

---

## Step 2: Register a User (First Time Only)

### In the Swagger UI (http://localhost:8000/docs):

1. **Find the `/auth/register` endpoint** (under "auth" section)
2. **Click "Try it out"**
3. **Enter user details:**
   ```json
   {
     "username": "myuser",
     "email": "myuser@example.com",
     "password": "mypassword123"
   }
   ```
4. **Click "Execute"**
5. **Copy the response** - you'll see user details (first user becomes admin automatically)

---

## Step 3: Login to Get JWT Token

1. **Find the `/auth/login` endpoint** (under "auth" section)
2. **Click "Try it out"**
3. **Enter credentials:**
   - `username`: `myuser`
   - `password`: `mypassword123`
4. **Click "Execute"**
5. **Copy the `access_token`** from the response (looks like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

---

## Step 4: Authorize in Swagger UI

1. **Click the green "Authorize" button** at the top right of the Swagger page
2. **Paste your `access_token`** in the "Value" field
3. **Click "Authorize"**
4. **Click "Close"**

Now all endpoints that require authentication will work!

---

## Step 5: Add a Proxy

### Option A: Using Swagger UI (Easiest)

1. **Find the `POST /proxies` endpoint** (under "proxies" section)
2. **Click "Try it out"**
3. **Enter proxy details:**
   ```json
   {
     "ip": "192.168.1.100",
     "port": 8080,
     "protocol": "http",
     "username": "optional_username",
     "password": "optional_password"
   }
   ```
4. **Click "Execute"**
5. **See the response** - your proxy is now added!

### Option B: Using curl (Command Line)

```bash
curl -X POST "http://localhost:8000/proxies" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{
    "ip": "192.168.1.100",
    "port": 8080,
    "protocol": "http"
  }'
```

Replace `YOUR_ACCESS_TOKEN_HERE` with your token from Step 3.

---

## Step 6: View All Proxies

1. **Find the `GET /proxies` endpoint**
2. **Click "Try it out"**
3. **Optional parameters:**
   - `working_only`: `false` (to see all proxies)
   - `limit`: `100` (max proxies to return)
   - `offset`: `0` (pagination)
4. **Click "Execute"**
5. **See all your proxies!**

---

## Step 7: Get a Proxy (Use Proxy Rotation)

### Get Random Proxy:
1. **Find `GET /proxy/random`**
2. **Click "Try it out"**
3. **Optional:** Add `target_url` to check blacklist
4. **Click "Execute"**
5. **Get a random working proxy!**

### Get Proxy by Strategy:
1. **Find `GET /proxy`**
2. **Click "Try it out"**
3. **Choose strategy:**
   - `random` - Random proxy
   - `round_robin` - Next proxy in rotation
   - `lru` - Least recently used
   - `best` - Lowest latency
4. **Click "Execute"**

---

## Step 8: Test a Proxy

1. **Find `POST /proxies/{proxy_id}/test`**
2. **Click "Try it out"**
3. **Enter the proxy ID** (from Step 6)
4. **Click "Execute"**
5. **See test results** - latency, status, etc.

---

## Example: Complete Workflow

### 1. Add Multiple Proxies:

```json
// Proxy 1
{
  "ip": "192.168.1.100",
  "port": 8080,
  "protocol": "http"
}

// Proxy 2
{
  "ip": "192.168.1.101",
  "port": 3128,
  "protocol": "http",
  "username": "user1",
  "password": "pass1"
}

// Proxy 3
{
  "ip": "10.0.0.50",
  "port": 8080,
  "protocol": "https"
}
```

### 2. View Proxy Statistics:

Visit: **http://localhost:8000/health/proxies**

Shows:
- Total proxies
- Working proxies
- Dead proxies
- Average latency
- Min/Max latency

---

## Using Proxies Programmatically

### Python Example:

```python
import httpx

# Get JWT token (from login)
token = "YOUR_ACCESS_TOKEN"

# Get a proxy
response = httpx.get(
    "http://localhost:8000/proxy?strategy=random",
    headers={"Authorization": f"Bearer {token}"}
)
proxy_data = response.json()

# Use the proxy
proxy_url = f"{proxy_data['protocol']}://{proxy_data['address']}"
proxies = {
    "http://": proxy_url,
    "https://": proxy_url
}

# Make request through proxy
response = httpx.get("https://httpbin.org/ip", proxies=proxies)
print(response.json())
```

### JavaScript/Node.js Example:

```javascript
const axios = require('axios');

const token = 'YOUR_ACCESS_TOKEN';

// Get a proxy
const proxyResponse = await axios.get('http://localhost:8000/proxy?strategy=random', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const proxy = proxyResponse.data;
const proxyUrl = `${proxy.protocol}://${proxy.address}`;

// Use the proxy
const response = await axios.get('https://httpbin.org/ip', {
  proxy: {
    host: proxy.ip,
    port: proxy.port,
    protocol: proxy.protocol
  }
});

console.log(response.data);
```

---

## Quick Reference

### Endpoints You'll Use Most:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/register` | POST | Create account |
| `/auth/login` | POST | Get JWT token |
| `/proxies` | POST | Add proxy |
| `/proxies` | GET | List all proxies |
| `/proxy` | GET | Get proxy (with strategy) |
| `/proxy/random` | GET | Get random proxy |
| `/proxy/best` | GET | Get best proxy |
| `/proxies/{id}/test` | POST | Test a proxy |
| `/health/proxies` | GET | View statistics |

---

## Troubleshooting

### "401 Unauthorized"
- Make sure you clicked "Authorize" in Swagger UI
- Check that your token is valid (login again if expired)

### "No working proxies available"
- Add at least one proxy first
- Test proxies to mark them as working
- Wait for automatic health checks (runs every 5 minutes)

### "Proxy already exists"
- Check existing proxies first
- Use different IP/port combination

---

## Tips

1. **First user is admin** - Can access `/admin` endpoints
2. **Proxies are tested automatically** - Health checks run every 5 minutes
3. **Use strategies** - Different strategies for different use cases
4. **Check blacklist** - Use `target_url` parameter to check if URL is blocked
5. **View logs** - Check `/logs` endpoint to see activity

---

## Next Steps

1. ✅ Add proxies
2. ✅ Test proxies
3. 📝 Set up blacklist rules (`/blacklist`)
4. 📝 View activity logs (`/logs`)
5. 📝 Configure rotation strategies

Happy proxying! 🚀


