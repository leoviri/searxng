#!/bin/bash

# SearXNG MCP Server - Railway Deployment Script

set -e

echo "🚀 SearXNG MCP Server - Railway Deployment Setup"
echo "================================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 Please log in to Railway:"
    railway login
fi

# Initialize Railway project if not already done
if [ ! -f "railway.toml" ]; then
    echo "❌ railway.toml not found in current directory"
    exit 1
fi

echo "📁 Initializing Railway project..."
railway init

# Generate a random secret key
SECRET_KEY=$(openssl rand -hex 32)

echo "🔧 Setting environment variables..."
railway variables set SEARXNG_SECRET_KEY="$SECRET_KEY"

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

# Get the deployment URL
echo "🌐 Getting deployment URL..."
RAILWAY_URL=$(railway status --json | jq -r '.deployments[0].url' 2>/dev/null || echo "")

if [ -n "$RAILWAY_URL" ]; then
    echo "✅ Deployment successful!"
    echo "📍 Your SearXNG instance is available at: $RAILWAY_URL"
    
    # Update the base URL environment variable
    echo "🔧 Updating base URL..."
    railway variables set SEARXNG_BASE_URL="$RAILWAY_URL"
    
    echo "📝 Updating MCP configuration..."
    sed "s|https://your-app-name.railway.app|$RAILWAY_URL|g" mcp-config-production.json > mcp-config-live.json
    
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo "✅ SearXNG deployed to: $RAILWAY_URL"
    echo "✅ JSON API enabled for MCP access"
    echo "✅ Environment variables configured"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Test your deployment: curl -I $RAILWAY_URL"
    echo "2. Test JSON API: curl \"$RAILWAY_URL/search?q=test&format=json\""
    echo "3. Update your MCP client with: mcp-config-live.json"
    echo "4. Add to Claude Desktop config with URL: $RAILWAY_URL"
else
    echo "⚠️ Could not retrieve deployment URL. Check Railway dashboard."
fi

echo ""
echo "📚 For detailed setup instructions, see: DEPLOY-RAILWAY.md" 