# 🚀 Complete Quick Start Guide

## ✅ What's New & Improved

### 1. **Health Score-Based Proxy Selection** ⭐
- **NEW**: Get the best proxy based on comprehensive health scoring
- **Strategy**: Use `strategy=health_score` to get the most reliable proxy
- **Score Range**: 0-100 (higher is better)
- **Factors**: Working status, latency, failure count, recency

### 2. **Web Scraping Ready** 🕷️
- Complete Python examples for web scraping
- Support for requests, httpx, BeautifulSoup, Selenium
- Automatic proxy rotation
- Error handling and retry logic

### 3. **Production Features** 🏭
- JWT authentication
- Rate limiting
- Activity logging
- Blacklist enforcement
- CSV export

---

## 📋 Quick Setup (3 Steps)

### Step 1: Start Server
```bash
./run_server.sh
```

### Step 2: Get API Token
1. Open: http://localhost:8000/docs
2. Register: `POST /auth/register`
3. Login: `POST /auth/login`
4. Copy `access_token`

### Step 3: Get Best Proxy
```bash
curl -X GET "http://localhost:8000/proxy?strategy=health_score" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 Key Features

### Health Score Strategy (Recommended)
```python
# Get best proxy based on health score
proxy = get_proxy(strategy="health_score")
# Returns proxy with highest health score (0-100)
```

### Available Strategies
- `health_score` - Best overall (recommended) ⭐
- `best` - Lowest latency
- `round_robin` - Even distribution
- `lru` - Least recently used
- `random` - Random selection

---

## 📖 Documentation Files

1. **HOW_TO_RUN.md** - Setup and installation
2. **HOW_TO_ADD_PROXIES.md** - Adding and managing proxies
3. **WEB_SCRAPING_GUIDE.md** - Complete web scraping examples
4. **JUDGES_PRESENTATION.md** - Presentation for judges/panel

---

## 🔥 Quick Examples

### Python: Get Best Proxy
```python
import requests

API_URL = "http://localhost:8000"
TOKEN = "YOUR_ACCESS_TOKEN"

response = requests.get(
    f"{API_URL}/proxy?strategy=health_score",
    headers={"Authorization": f"Bearer {TOKEN}"}
)
proxy_data = response.json()

print(f"Proxy: {proxy_data['address']}")
print(f"Health Score: {proxy_data['health_score']:.2f}/100")
print(f"Latency: {proxy_data.get('latency', 'N/A')}ms")
```

### Python: Web Scraping
```python
import requests

# Get best proxy
proxy_response = requests.get(
    "http://localhost:8000/proxy?strategy=health_score",
    headers={"Authorization": f"Bearer {TOKEN}"}
)
proxy_data = proxy_response.json()

# Build proxy URL
proxy_url = f"{proxy_data['protocol']}://{proxy_data['address']}"
proxies = {"http": proxy_url, "https": proxy_url}

# Scrape
response = requests.get(
    "https://example.com",
    proxies=proxies,
    timeout=30
)
print(response.text)
```

---

## 🎓 For Judges/Panel

See **JUDGES_PRESENTATION.md** for:
- Executive summary
- Technical architecture
- Health score algorithm
- Use cases
- Performance metrics
- Demonstration scenarios

---

## 🆘 Need Help?

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Statistics**: http://localhost:8000/health/proxies

---

**Ready to start? Run `./run_server.sh` and visit http://localhost:8000/docs** 🚀

