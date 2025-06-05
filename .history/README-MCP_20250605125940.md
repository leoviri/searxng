# SearXNG MCP Server

This repository contains an MCP (Model Context Protocol) server that provides search functionality using SearXNG as the backend. This allows AI assistants and language models to perform web searches through a privacy-focused, metasearch engine.

## Features

- **Web Search**: General web search across multiple search engines
- **Image Search**: Specialized image search functionality  
- **News Search**: Search for current news articles
- **Privacy-focused**: Uses SearXNG which doesn't track users
- **Configurable**: Supports custom search engines, categories, and languages
- **Local**: Runs entirely on your own infrastructure

## Prerequisites

1. **SearXNG instance**: You need a running SearXNG instance with JSON API enabled
2. **Python 3.8+**: For running the MCP server
3. **MCP-compatible client**: Such as Claude Desktop, Cursor, or other MCP-enabled applications

## Quick Start

### 1. Set up SearXNG with JSON API

First, ensure your SearXNG instance has JSON format enabled in its configuration:

```yaml
search:
  formats:
    - html
    - json
```

### 2. Install Dependencies

```bash
pip install -r requirements-mcp.txt
```

### 3. Run the MCP Server

```bash
python searxng_mcp_server.py
```

Or specify a custom SearXNG URL:

```bash
python searxng_mcp_server.py http://your-searxng-instance.com
```

### 4. Configure Your MCP Client

Add the server configuration to your MCP client's config. For Claude Desktop, add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "searxng": {
      "command": "python",
      "args": ["/path/to/searxng_mcp_server.py"],
      "env": {
        "SEARXNG_URL": "http://localhost:8080"
      }
    }
  }
}
```

## Available Tools

### 1. `search`
General web search functionality.

**Parameters:**
- `query` (required): Search query
- `categories` (optional): Search categories (general, images, videos, news, music, files, it, science, social media)
- `language` (optional): Search language (e.g., 'en', 'fr', 'de')
- `max_results` (optional): Maximum number of results (1-50, default: 10)
- `engines` (optional): Specific search engines to use (comma-separated)

### 2. `search_images`
Specialized image search.

**Parameters:**
- `query` (required): Image search query
- `max_results` (optional): Maximum number of results (1-30, default: 10)

### 3. `search_news`
Search for news articles.

**Parameters:**
- `query` (required): News search query
- `max_results` (optional): Maximum number of results (1-30, default: 10)

## Example Usage in AI Assistant

Once configured, you can ask your AI assistant to search for information:

- "Search for recent developments in AI"
- "Find images of sustainable architecture"
- "Search for news about renewable energy"
- "Look up Python tutorials for beginners"

## Configuration Options

### SearXNG Configuration

Ensure your SearXNG instance is configured properly:

1. **JSON API enabled**: Add `json` to the `formats` list in your settings
2. **Search engines**: Configure which search engines to use
3. **Categories**: Enable the categories you want to search
4. **Language support**: Configure supported languages

### MCP Server Configuration

You can customize the MCP server by:

1. **Changing the SearXNG URL**: Pass as command line argument
2. **Modifying search parameters**: Edit the default values in the server code
3. **Adding new search types**: Extend the server with additional tools

## Docker Deployment

You can also run the entire setup using Docker:

```bash
# Run SearXNG with JSON API enabled
docker run -d -p 8080:8080 -v $(pwd)/searxng-settings.yml:/etc/searxng/settings.yml searxng/searxng:latest

# Run the MCP server
python searxng_mcp_server.py http://localhost:8080
```

## Security Considerations

1. **Local deployment**: Run SearXNG locally to maintain privacy
2. **Network access**: Ensure the MCP server can access your SearXNG instance
3. **Authentication**: SearXNG doesn't require authentication by default, but you can add it
4. **Rate limiting**: Consider implementing rate limiting for production use

## Troubleshooting

### Common Issues

1. **Connection refused**: Ensure SearXNG is running and accessible
2. **JSON format not available**: Check that JSON is enabled in SearXNG settings
3. **No results**: Verify that search engines are configured and working
4. **MCP client not connecting**: Check the configuration file path and syntax

### Debug Mode

Run the server with debug logging:

```bash
PYTHONPATH=. python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import asyncio
from searxng_mcp_server import main
asyncio.run(main())
"
```

## Contributing

Contributions are welcome! Areas for improvement:

1. **Additional search types**: Video search, file search, etc.
2. **Enhanced formatting**: Better result presentation
3. **Caching**: Add result caching for better performance
4. **Error handling**: More robust error handling and recovery
5. **Configuration**: More configurable options

## License

This project follows the same license as SearXNG (AGPL-3.0).

## Related Projects

- [SearXNG](https://github.com/searxng/searxng): Privacy-respecting metasearch engine
- [Model Context Protocol](https://modelcontextprotocol.io/): Protocol for connecting AI to external tools
- [Claude Desktop](https://claude.ai/): AI assistant that supports MCP servers 