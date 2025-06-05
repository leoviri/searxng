# Deploying SearXNG MCP Server to Railway

This guide will help you deploy your SearXNG MCP Server to Railway for production use.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Push your code to a GitHub repository
3. **Railway CLI** (optional): Install with `npm install -g @railway/cli`

## Deployment Steps

### 1. Prepare Your Repository

Ensure these files are in your repository:
- `railway.toml` - Railway configuration
- `Dockerfile.railway` - Production Dockerfile
- `searxng-settings-production.yml` - Production settings
- `searxng_mcp_server.py` - MCP server code

### 2. Deploy to Railway

#### Option A: Using Railway Dashboard (Recommended)

1. **Connect Repository**:
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository

2. **Configure Environment Variables**:
   - In your Railway project dashboard, go to "Variables"
   - Add these variables:
   ```
   SEARXNG_SECRET_KEY=your-super-secret-key-here
   SEARXNG_BASE_URL=https://your-app-name.railway.app
   ```

3. **Update Base URL**:
   - After first deployment, Railway will give you a domain
   - Update `SEARXNG_BASE_URL` with your actual Railway domain

#### Option B: Using Railway CLI

1. **Login and Initialize**:
   ```bash
   railway login
   railway init
   ```

2. **Set Environment Variables**:
   ```bash
   railway variables set SEARXNG_SECRET_KEY=your-super-secret-key-here
   railway variables set SEARXNG_BASE_URL=https://your-app-name.railway.app
   ```

3. **Deploy**:
   ```bash
   railway up
   ```

### 3. Configure Your MCP Client

After deployment, update your MCP client configuration:

**For Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "searxng": {
      "command": "python",
      "args": ["/path/to/searxng_mcp_server.py"],
      "env": {
        "SEARXNG_URL": "https://your-actual-railway-domain.railway.app"
      }
    }
  }
}
```

### 4. Test Your Deployment

1. **Check SearXNG Web Interface**:
   - Visit your Railway domain
   - Verify the search interface loads

2. **Test JSON API**:
   ```bash
   curl "https://your-domain.railway.app/search?q=test&format=json"
   ```

3. **Test MCP Server**:
   - Use your MCP client to perform a search
   - Verify results are returned properly

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SEARXNG_SECRET_KEY` | Yes | Secret key for SearXNG | `super-secret-key-123` |
| `SEARXNG_BASE_URL` | Yes | Your Railway domain | `https://myapp.railway.app` |
| `PORT` | No | Port (set by Railway) | `8080` |

## Production Considerations

### Security
- **Generate a strong secret key**: Use a long, random string
- **HTTPS Only**: Railway provides HTTPS by default
- **Rate Limiting**: Consider adding rate limiting for public instances

### Performance
- **Image Proxy**: Enabled in production config for better performance
- **Static File Hashing**: Enabled for better caching
- **HTTP/1.1**: Used for better compatibility

### Monitoring
- **Railway Logs**: Check deployment logs in Railway dashboard
- **Health Checks**: Railway will monitor your service health
- **Error Tracking**: Monitor MCP server logs for any issues

## Troubleshooting

### Common Issues

1. **Deployment Fails**:
   - Check Railway build logs
   - Ensure all required files are in repository
   - Verify Dockerfile.railway syntax

2. **JSON API Returns 403**:
   - Verify `json` is in formats list in production settings
   - Check SearXNG logs in Railway

3. **MCP Client Can't Connect**:
   - Verify SEARXNG_URL in MCP config matches Railway domain
   - Test API endpoint manually with curl

4. **Search Returns No Results**:
   - Check that search engines are configured and working
   - Verify network connectivity from Railway

### Debug Commands

**Check service status**:
```bash
curl -I https://your-domain.railway.app/
```

**Test JSON API**:
```bash
curl "https://your-domain.railway.app/search?q=python&format=json" | head -20
```

**Check Railway logs**:
```bash
railway logs
```

## Scaling and Optimization

### Resource Usage
- **Memory**: SearXNG typically uses 100-300MB RAM
- **CPU**: Low CPU usage for typical search loads
- **Storage**: Minimal storage requirements

### Railway Plans
- **Hobby Plan**: Good for personal use
- **Pro Plan**: Recommended for team/production use
- **Custom Resources**: Available for high-traffic scenarios

### Caching (Optional)
To improve performance, you can add Redis caching:

1. **Add Railway Redis**:
   ```bash
   railway add redis
   ```

2. **Update production settings**:
   ```yaml
   redis:
     url: $REDIS_URL
   ```

## Support

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **SearXNG Documentation**: [docs.searxng.org](https://docs.searxng.org)
- **MCP Documentation**: [modelcontextprotocol.io](https://modelcontextprotocol.io)

## Next Steps

After successful deployment:
1. Configure your MCP client with the production URL
2. Test search functionality thoroughly
3. Monitor performance and logs
4. Consider adding custom domains if needed
5. Set up monitoring/alerting for production use 