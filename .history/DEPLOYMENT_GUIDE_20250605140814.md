# SearXNG MCP Online Deployment Guide

This guide explains how to deploy your SearXNG MCP server fully online using Railway.

## 🚀 **Quick Setup**

### **1. Deploy to Railway**

1. **Connect Repository to Railway:**
   - Go to [Railway.app](https://railway.app)
   - Create a new project
   - Connect your GitHub repository: `/Users/leonardoviri/lab/searxng`

2. **Set Environment Variables:**
   ```
   SEARXNG_URL=https://searx.be
   PORT=8000
   ```

3. **Deploy Files:**
   - `searxng_web_server.py` - Main FastAPI web server
   - `requirements.txt` - Python dependencies  
   - `Procfile` - Railway deployment command
   - `railway.json` - Railway configuration

### **2. Update Your MCP Configuration**

Your current MCP config should work, but make sure the URL matches your Railway deployment:

```json
{
  "searxng": {
    "command": "python",
    "args": ["/Users/leonardoviri/lab/searxng/searxng_mcp_client.py"],
    "env": {
      "SEARXNG_MCP_WEB_URL": "https://YOUR-APP-NAME.up.railway.app"
    },
    "tags": ["search", "web", "metasearch"]
  }
}
```

## 🛠️ **Architecture Overview**

```
Your MCP Client (Local)
        ↓ HTTP Requests
Railway Web Server (Online)
        ↓ SearXNG API Calls  
SearXNG Instance (Public)
```

### **Components:**

1. **`searxng_mcp_client.py`** - Local MCP client that forwards requests to web server
2. **`searxng_web_server.py`** - FastAPI web server deployed on Railway  
3. **Public SearXNG** - Uses `https://searx.be` as the search backend

## 🔧 **API Endpoints**

Once deployed, your Railway app will expose:

- **`GET /`** - API information
- **`GET /health`** - Health check
- **`GET /tools`** - List available search tools
- **`POST /tools/search`** - General web search
- **`POST /tools/search_images`** - Image search
- **`POST /tools/search_news`** - News search  
- **`POST /tools/search_videos`** - Video search
- **`POST /tools/search_science`** - Scientific paper search
- **`POST /tools/advanced_search`** - Advanced search with operators

## 🌐 **Environment Variables**

### **Railway Deployment:**
- `SEARXNG_URL` - SearXNG backend URL (default: `https://searx.be`)
- `PORT` - Server port (Railway sets this automatically)

### **Local MCP Client:**
- `SEARXNG_MCP_WEB_URL` - Your Railway app URL

## 📋 **Testing Your Deployment**

### **1. Test Web Server Directly:**
```bash
curl https://YOUR-APP-NAME.up.railway.app/health
```

### **2. Test Search Endpoint:**
```bash
curl -X POST https://YOUR-APP-NAME.up.railway.app/tools/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test search", "max_results": 5}'
```

### **3. Test MCP Client:**
Your MCP client should now work with the online service!

## 🔄 **Deployment Steps**

### **Step 1: Deploy to Railway**
```bash
# Push your code to GitHub
git add .
git commit -m "Add web server deployment"  
git push

# Deploy on Railway (connected to your GitHub repo)
```

### **Step 2: Get Your URL**
After deployment, Railway will give you a URL like:
`https://searxng-production-XXXX.up.railway.app`

### **Step 3: Update MCP Config**
Update your `~/.cursor/mcp.json` with the Railway URL:
```json
"env": {
  "SEARXNG_MCP_WEB_URL": "https://searxng-production-XXXX.up.railway.app"
}
```

### **Step 4: Test Everything**
Your MCP client will now make requests to the online Railway service!

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **"Connection refused"**
   - Check Railway deployment logs
   - Verify environment variables are set

2. **"Tool not found"**  
   - Ensure Railway app is running
   - Check `/tools` endpoint returns tools list

3. **"SearXNG backend error"**
   - Verify `SEARXNG_URL` environment variable
   - Test SearXNG backend directly

### **Debug Commands:**
```bash
# Check Railway logs
railway logs

# Test health endpoint
curl https://YOUR-APP.up.railway.app/health

# List available tools
curl https://YOUR-APP.up.railway.app/tools
```

## ✅ **Benefits of Online Deployment**

- **🌐 Fully Online** - No local dependencies
- **⚡ Fast** - Railway hosting with global CDN
- **🔄 Scalable** - Handles multiple concurrent requests
- **🛡️ Reliable** - Railway's infrastructure and monitoring
- **🔧 Easy Updates** - Git push to deploy changes

## 🎯 **Next Steps**

1. **Deploy to Railway** following the steps above
2. **Update your MCP configuration** with the Railway URL
3. **Test the full integration** 
4. **Use your GPT** with the online SearXNG MCP service!

Your SearXNG MCP server is now **fully online** and ready for production use! 🚀 