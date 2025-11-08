#!/bin/bash

# Setup and Run Script for Proxy Manager
# This script will set up and run the project on your macOS system

set -e  # Exit on error

echo "🚀 Setting up Proxy Manager Project..."
echo ""

# Step 1: Check Python version
echo "📋 Step 1: Checking Python version..."
python3 --version
echo ""

# Step 2: Install dependencies
echo "📦 Step 2: Installing dependencies..."
echo "Installing proxy_manager dependencies..."
cd proxy_manager
pip3 install -e . --quiet
cd ..

echo "Installing mitm_forwarder dependencies..."
cd mitm_forwarder
pip3 install -r requirements.txt --quiet
cd ..

echo "✅ Dependencies installed!"
echo ""

# Step 3: Create .env file if it doesn't exist
echo "⚙️  Step 3: Setting up environment file..."
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
TEST_URL=https://httpbin.org/ip
CHECK_INTERVAL=300
MAX_THREADS=20
ROTATION_STRATEGY=round_robin
DB_URL=sqlite:///./proxy_manager.db
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
SYSTEM_TOKEN=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
EOF
    # Generate actual secrets
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
    SYSTEM_TOKEN=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
    cat > .env << EOF
TEST_URL=https://httpbin.org/ip
CHECK_INTERVAL=300
MAX_THREADS=20
ROTATION_STRATEGY=round_robin
DB_URL=sqlite:///./proxy_manager.db
SECRET_KEY=${SECRET_KEY}
SYSTEM_TOKEN=${SYSTEM_TOKEN}
EOF
    echo "✅ .env file created with secure tokens!"
else
    echo "✅ .env file already exists, skipping..."
fi
echo ""

# Step 4: Display next steps
echo "🎉 Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 NEXT STEPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Start the server by running:"
echo "   python3 -m uvicorn proxy_manager.src.proxy_manager.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. Open your browser and visit:"
echo "   http://localhost:8000/docs"
echo ""
echo "3. To stop the server, press Ctrl+C"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"


