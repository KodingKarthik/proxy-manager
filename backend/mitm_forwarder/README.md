# mitmproxy Forwarder Addon

A production-ready mitmproxy addon that integrates with a FastAPI proxy manager backend to forward HTTP/HTTPS traffic through managed upstream proxies with blacklist enforcement and activity logging.

## Overview

This addon intercepts HTTP/HTTPS requests, validates them against blacklist rules, requests upstream proxies from a FastAPI backend, forwards requests through those proxies, and logs activity back to the backend.

## Features

- **Request Interception**: Intercepts all HTTP/HTTPS traffic through mitmproxy
- **Blacklist Enforcement**: Validates requests against regex-based blacklist rules
- **Proxy Rotation**: Requests upstream proxies from FastAPI backend per request
- **Activity Logging**: Logs all requests to FastAPI backend for auditing
- **Streaming Support**: Handles large responses with streaming
- **Error Handling**: Graceful error handling with appropriate HTTP status codes
- **Rate Limiting**: Configurable concurrent request limits

## Architecture

```
Client → mitmproxy (addon) → FastAPI Backend (get proxy)
                              ↓
                         Upstream Proxy → Target Server
                              ↓
                         Response → Client
                              ↓
                         Activity Log → FastAPI Backend
```

## Requirements

- Python 3.11+
- mitmproxy 10.1.5+
- FastAPI backend with proxy management endpoints
- System token for FastAPI authentication

## Installation

### From Source

```bash
cd mitm_forwarder
pip install -r requirements.txt
```

### Docker

```bash
docker build -t mitm-forwarder .
```

## Configuration

Configuration is managed through environment variables or a `.env` file:

### Required Variables

- `SYSTEM_TOKEN`: System token for FastAPI authentication (required for blacklist and activity endpoints)

### Optional Variables

- `FASTAPI_BASE_URL`: FastAPI backend base URL (default: `http://127.0.0.1:8000`)
- `FASTAPI_PROXY_ENDPOINT`: Proxy endpoint path (default: `/proxy`)
- `FASTAPI_BLACKLIST_ENDPOINT`: Blacklist endpoint path (default: `/blacklist`)
- `FASTAPI_ACTIVITY_ENDPOINT`: Activity logging endpoint path (default: `/activity`)
- `BLACKLIST_REFRESH_SECONDS`: Blacklist cache refresh interval (default: `60`)
- `HTTPX_TIMEOUT`: HTTP request timeout in seconds (default: `30.0`)
- `MITM_LISTEN_PORT`: Port for mitmproxy to listen on (default: `8080`)
- `MAX_CONCURRENT_REQUESTS`: Maximum concurrent outbound requests (default: `100`)
- `REQUIRE_USER_JWT`: Require user JWT in Authorization header (default: `True`)
- `DEFAULT_USER_JWT`: Default user JWT to use if client doesn't provide Authorization header (optional)

### Example `.env` file

```env
SYSTEM_TOKEN=your-system-token-here
FASTAPI_BASE_URL=http://127.0.0.1:8000
BLACKLIST_REFRESH_SECONDS=60
HTTPX_TIMEOUT=30.0
MITM_LISTEN_PORT=8080
MAX_CONCURRENT_REQUESTS=100
REQUIRE_USER_JWT=true
# DEFAULT_USER_JWT=Bearer your-default-jwt-token  # Optional: use if clients don't send JWT
```

## Usage

### Running Locally

```bash
# Set environment variables
export SYSTEM_TOKEN=your-system-token

# Run mitmdump with the addon
mitmdump -s mitm_forwarder_addon.py -p 8080
```

### Running with Docker

```bash
docker run -d \
  -p 8080:8080 \
  -e SYSTEM_TOKEN=your-system-token \
  -e FASTAPI_BASE_URL=http://api:8000 \
  mitm-forwarder
```

### Client Configuration

**IMPORTANT**: Clients MUST include their JWT token in the `Authorization` header. The addon forwards this JWT to FastAPI for user authentication.

Clients need to configure their HTTP client to use mitmproxy as a proxy:

#### Using curl

```bash
curl -x http://localhost:8080 https://example.com \
  -H "Authorization: Bearer YOUR_USER_JWT"
```

#### Using Python requests

```python
import requests

proxies = {
    'http': 'http://localhost:8080',
    'https': 'http://localhost:8080'
}

headers = {
    'Authorization': 'Bearer YOUR_USER_JWT'
}

response = requests.get('https://example.com', proxies=proxies, headers=headers)
```

#### Using httpx

```python
import httpx

proxies = "http://localhost:8080"

headers = {
    'Authorization': 'Bearer YOUR_USER_JWT'
}

async with httpx.AsyncClient(proxies=proxies, headers=headers) as client:
    response = await client.get('https://example.com')
```

## Authentication Flow

1. **Client sends request** with `Authorization: Bearer {USER_JWT}` header
2. **mitmproxy addon** extracts the JWT from the client's Authorization header
3. **Addon calls FastAPI** `/proxy` endpoint with the user's JWT in the `Authorization` header
4. **FastAPI authenticates** the user using the JWT and returns a proxy
5. **Addon forwards** the request through the returned proxy
6. **Activity is logged** with the authenticated user's ID

**Note**: If `REQUIRE_USER_JWT=true` (default) and client doesn't send Authorization header, the request is rejected with 401. Set `DEFAULT_USER_JWT` to use a fallback JWT.

## FastAPI Backend Integration

The addon expects the FastAPI backend to provide the following endpoints:

### GET `/proxy`

Returns an upstream proxy for forwarding requests.

**Headers:**
- `Authorization: {USER_JWT}` (required, user's JWT token from client request)

**Query Parameters:**
- `target_url` (optional): Target URL for blacklist checking

**Response:**
```json
{
  "id": 42,
  "ip": "1.2.3.4",
  "port": 8080,
  "address": "1.2.3.4:8080",
  "protocol": "http",
  "is_working": true
}
```

**Status Codes:**
- `200`: Proxy returned successfully
- `403`: Target URL is blacklisted
- `404`: No working proxies available

### GET `/blacklist`

Returns list of blacklist regex patterns.

**Headers:**
- `Authorization: Bearer {SYSTEM_TOKEN}` (required)

**Response:**
```json
[
  {
    "id": 1,
    "pattern": "^.*facebook\\.com.*$",
    "description": "Block Facebook",
    "created_at": "2024-01-01T00:00:00",
    "created_by": 1
  }
]
```

### POST `/activity`

Accepts activity logs from the addon.

**Headers:**
- `Authorization: Bearer {SYSTEM_TOKEN}` (required)
- `Content-Type: application/json`

**Request Body:**
```json
{
  "user_id": 7,
  "endpoint": "https://example.com/path",
  "method": "GET",
  "status_code": 200,
  "target_url": "https://example.com/path",
  "proxy_id": 42,
  "timestamp": 1690000000.0
}
```

## Security Considerations

### TLS Interception

⚠️ **IMPORTANT**: This addon performs TLS interception. Clients must:

1. **Consent to interception**: Ensure all clients understand their traffic is being intercepted
2. **Install mitmproxy certificate**: Clients must install mitmproxy's CA certificate
3. **Legal compliance**: Ensure compliance with local laws and regulations regarding traffic interception

### Certificate Installation

1. Start mitmproxy: `mitmdump -s mitm_forwarder_addon.py -p 8080`
2. Visit `http://mitm.it` in a browser configured to use the proxy
3. Download and install the CA certificate for your platform
4. Trust the certificate in your system's certificate store

### Token Security

- The `SYSTEM_TOKEN` should be kept secret and rotated regularly (used for blacklist/activity endpoints)
- User JWTs are required in the `Authorization` header for proxy requests
- User JWTs are forwarded to FastAPI for authentication
- Authorization headers are masked in logs
- If `REQUIRE_USER_JWT=true`, requests without Authorization header are rejected

## Error Handling

The addon handles various error conditions:

- **Blacklisted URL**: Returns `403 Forbidden` and logs activity
- **No Proxy Available**: Returns `502 Bad Gateway` and logs activity
- **Proxy Error**: Returns `502 Bad Gateway` and logs activity
- **Timeout**: Returns `504 Gateway Timeout` and logs activity
- **Network Error**: Returns `502 Bad Gateway` and logs activity

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Troubleshooting

### Addon not loading

- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify `SYSTEM_TOKEN` is set in environment
- Check mitmproxy logs for errors

### No proxy available

- Verify FastAPI backend is running and accessible
- Check `FASTAPI_BASE_URL` is correct
- Verify `SYSTEM_TOKEN` is valid
- Check FastAPI logs for errors

### Blacklist not working

- Verify blacklist rules are loaded: Check logs for "Refreshed blacklist cache"
- Check blacklist patterns are valid regex
- Verify `FASTAPI_BLACKLIST_ENDPOINT` is correct

### Activity logs not posting

- Activity logging is fire-and-forget and won't block requests
- Check FastAPI logs for activity endpoint errors
- Verify `FASTAPI_ACTIVITY_ENDPOINT` is correct

## Development

### Project Structure

```
mitm_forwarder/
├── mitm_forwarder_addon.py  # Main addon script
├── config.py                # Configuration management
├── proxy_client.py          # FastAPI client
├── blacklist_cache.py       # Blacklist caching
├── logger.py                # Logging utilities
├── requirements.txt         # Dependencies
├── Dockerfile              # Container image
├── README.md               # This file
└── tests/                  # Unit tests
    ├── conftest.py
    ├── test_blacklist.py
    └── test_proxy_client.py
```

## License

MIT

