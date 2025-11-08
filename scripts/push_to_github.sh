#!/bin/bash

# Script to push project to GitHub
# Usage: ./push_to_github.sh YOUR_REPO_NAME

set -e

REPO_NAME=${1:-"proxy-manager"}

echo "🚀 Pushing to GitHub: KodingKarthik/$REPO_NAME"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "❌ Git not initialized. Run: git init"
    exit 1
fi

# Add all files
echo "📦 Adding files..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit."
else
    # Commit changes
    echo "💾 Committing changes..."
    git commit -m "Initial commit: Multi-Threaded Rotating Proxy Manager with Health Score System

Features:
- Intelligent health score-based proxy selection (0-100 scale)
- Multi-threaded proxy health monitoring
- Multiple rotation strategies (health_score, best, round_robin, lru, random)
- RESTful API with FastAPI
- JWT authentication and authorization
- Rate limiting and activity logging
- Blacklist enforcement
- Web scraping examples and guides
- Complete documentation for judges/panel"
fi

# Check if remote exists
if git remote get-url origin &>/dev/null; then
    echo "ℹ️  Remote 'origin' already exists."
    read -p "Update remote to https://github.com/KodingKarthik/$REPO_NAME.git? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin "https://github.com/KodingKarthik/$REPO_NAME.git"
        echo "✅ Remote updated."
    fi
else
    echo "🔗 Adding remote..."
    git remote add origin "https://github.com/KodingKarthik/$REPO_NAME.git"
    echo "✅ Remote added."
fi

# Set branch to main
git branch -M main

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Create repository on GitHub:"
echo "   Go to: https://github.com/new"
echo "   Repository name: $REPO_NAME"
echo "   Description: Multi-Threaded Rotating Proxy Manager with Intelligent Health Score System"
echo "   Choose: Public or Private"
echo "   DON'T initialize with README"
echo "   Click 'Create repository'"
echo ""
echo "2. Push to GitHub:"
echo "   git push -u origin main"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Have you created the repository on GitHub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Pushing to GitHub..."
    git push -u origin main
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "📦 Repository: https://github.com/KodingKarthik/$REPO_NAME"
else
    echo "⏸️  Please create the repository first, then run:"
    echo "   git push -u origin main"
fi

