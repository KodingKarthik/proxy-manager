# ⚡ Quick Start: Web Scraping with Health Score Proxy

## 🎯 Goal: Connect to proxy by health score and scrape websites

---

## ✅ 3-Step Quick Start

### Step 1: Start Server

```bash
./run_server.sh
```

**Keep terminal open!**

---

### Step 2: Run Test Script

**Open new terminal:**

```bash
python3 simple_proxy_test.py
```

**This will:**
- ✅ Auto-login (or register)
- ✅ Get best proxy by **health score**
- ✅ Test connection
- ✅ Show proxy details

---

### Step 3: Run Full Example

```bash
python3 web_scraping_with_proxy.py
```

**This demonstrates:**
- ✅ Getting proxy by health score
- ✅ Web scraping examples
- ✅ Error handling

---

## 📊 What is Health Score?

**Health Score (0-100)** = Best proxy selection based on:
- ✅ Working status (40 pts)
- ✅ Latency (30 pts)
- ✅ Failure count (20 pts)
- ✅ Recency (10 pts)

**Always use `strategy=health_score`!**

---

## 🔧 Manual Usage

### Get Best Proxy

```bash
# 1. Login
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo_user&password=demo123456" | jq -r '.access_token')

# 2. Get best proxy by health score
curl -X GET "http://localhost:8000/proxy?strategy=health_score" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🐍 Python Example

```python
from web_scraping_with_proxy import ProxyManagerClient, scrape_with_proxy

# Initialize
client = ProxyManagerClient()
client.login("demo_user", "demo123456")

# Get best proxy by health score
proxy = client.get_best_proxy(strategy="health_score")

# Scrape website
response = scrape_with_proxy("https://example.com", proxy)
print(response.text)
```

---

## 📖 Full Documentation

- **`WORKING_WEB_SCRAPING.md`** - Complete guide
- **`WEB_SCRAPING_GUIDE.md`** - Detailed examples
- **`DEMONSTRATION_GUIDE.md`** - Step-by-step demo

---

**Ready to scrape! 🕷️**


