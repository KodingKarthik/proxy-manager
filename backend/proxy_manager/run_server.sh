#!/bin/bash
source venv/bin/activate
echo "🚀 Starting Proxy Manager Server..."
echo "📍 Server: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
python3 -m uvicorn proxy_manager.src.proxy_manager.main:app --reload --host 0.0.0.0 --port 8000
