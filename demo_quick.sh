#!/bin/bash

# Quick demonstration script
# Shows how to use the API via curl commands

API_URL="http://localhost:8000"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 PROXY MANAGER QUICK DEMONSTRATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Register (if needed)
echo "📝 Step 1: Registering user..."
echo "   Run: curl -X POST \"$API_URL/auth/register\" -H \"Content-Type: application/json\" -d '{\"username\":\"demo\",\"email\":\"demo@example.com\",\"password\":\"demo123\"}'"
echo ""

# Step 2: Login
echo "🔐 Step 2: Login to get token..."
echo "   Run: curl -X POST \"$API_URL/auth/login\" -H \"Content-Type: application/x-www-form-urlencoded\" -d \"username=demo&password=demo123\""
echo ""
echo "   ⚠️  Copy the 'access_token' from the response!"
echo ""

read -p "Enter your access token: " TOKEN

if [ -z "$TOKEN" ]; then
    echo "❌ Error: Token is required"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 3: Add proxy
echo "📡 Step 3: Adding a proxy..."
read -p "Enter proxy IP: " PROXY_IP
read -p "Enter proxy port (default 8080): " PROXY_PORT
PROXY_PORT=${PROXY_PORT:-8080}

echo ""
echo "Adding proxy $PROXY_IP:$PROXY_PORT..."
curl -X POST "$API_URL/proxies" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"ip\": \"$PROXY_IP\",
    \"port\": $PROXY_PORT,
    \"protocol\": \"http\"
  }" | python3 -m json.tool

echo ""
echo ""

# Step 4: Get best proxy
echo "⭐ Step 4: Getting best proxy (health score)..."
curl -X GET "$API_URL/proxy?strategy=health_score" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Demonstration complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

