# Multi-Threaded Rotating Proxy Manager

A production-ready FastAPI application for managing and rotating HTTP/HTTPS proxies with multi-threaded testing, health checks, and multiple rotation strategies.

## Features

- **Proxy CRUD Operations**: Add, list, and delete proxies via REST API
- **Multi-Threaded Testing**: Concurrent proxy health checking using ThreadPoolExecutor
- **Multiple Rotation Strategies**: Random, Round-Robin, LRU, and Best (lowest latency)
- **Automatic Health Checks**: Periodic background health monitoring with APScheduler
- **Proxy Metadata**: Track latency, last checked time, working status, and failure counts
- **SQLite Persistence**: Store proxy data in a local database using SQLModel

## Tech Stack

- Python 3.11+
- FastAPI
- Uvicorn (ASGI server)
- httpx (async HTTP client)
- SQLModel (database ORM)
- APScheduler (periodic health checks)
- Pydantic (configuration and validation)

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd CapProj
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (create it manually with the following content):
```bash
# Create .env file
cat > .env << EOF
TEST_URL=https://httpbin.org/ip
CHECK_INTERVAL=300
MAX_THREADS=20
ROTATION_STRATEGY=round_robin
DB_URL=sqlite:///./proxy_manager.db
EOF
```

Or manually create `.env` with:
```env
TEST_URL=https://httpbin.org/ip
CHECK_INTERVAL=300
MAX_THREADS=20
ROTATION_STRATEGY=round_robin
DB_URL=sqlite:///./proxy_manager.db
```

## Usage

### Start the Server

```bash
uvicorn proxy_manager.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Proxy Management

#### Add a Proxy
```bash
POST /proxies
Content-Type: application/json

{
  "ip": "192.168.1.1",
  "port": 8080,
  "username": "user",  # optional
  "password": "pass"    # optional
}
```

#### List All Proxies
```bash
GET /proxies?working_only=false&limit=100&offset=0
```

#### Delete a Proxy
```bash
DELETE /proxies/{id}
```

#### Test a Specific Proxy
```bash
POST /proxies/{id}/test
```

### Proxy Rotation

#### Get a Proxy (with strategy)
```bash
GET /proxy?strategy=random
GET /proxy?strategy=round_robin
GET /proxy?strategy=lru
GET /proxy?strategy=best
```

#### Get Next Proxy (Round-Robin)
```bash
GET /proxy/next
```

#### Get Random Proxy
```bash
GET /proxy/random
```

#### Get Best Proxy (Lowest Latency)
```bash
GET /proxy/best
```

### Health Checks

#### Application Health
```bash
GET /health
```

#### Proxy Pool Statistics
```bash
GET /health/proxies
```

## Rotation Strategies

- **random**: Selects a random working proxy
- **round_robin**: Cycles through proxies in order
- **lru**: Returns the least recently used proxy
- **best**: Returns the proxy with the lowest latency

## Configuration

All configuration is managed through environment variables (see `.env.example`):

- `TEST_URL`: URL used to test proxy connectivity
- `CHECK_INTERVAL`: Seconds between automatic health checks
- `MAX_THREADS`: Maximum concurrent threads for proxy testing
- `ROTATION_STRATEGY`: Default rotation strategy
- `DB_URL`: SQLite database connection string

## Project Structure

```
proxy_manager/
├── main.py              # FastAPI app entry point
├── database.py          # SQLModel engine and session setup
├── models.py            # Proxy model and Pydantic schemas
├── crud.py              # Database CRUD operations
├── scheduler.py         # APScheduler health check scheduler
├── routers/
│   ├── proxy_routes.py  # Proxy management endpoints
│   └── health_routes.py # Health check endpoints
└── utils/
    ├── config.py        # Configuration management
    ├── proxy_tester.py  # Multi-threaded proxy tester
    └── rotation.py      # Rotation strategy manager
```

## Development

The application automatically:
- Creates database tables on startup
- Starts the health check scheduler
- Tests proxies concurrently using multiple threads
- Updates proxy status based on health check results

## License

MIT

