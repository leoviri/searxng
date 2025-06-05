#!/usr/bin/env python3
"""
SearXNG MCP HTTP Client

An MCP client that connects to the web-based SearXNG MCP server via HTTP.
This allows using the MCP server deployed on Railway.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List

import httpx
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("searxng-mcp-client")

class SearXNGMCPClient:
    def __init__(self, web_server_url: str):
        self.web_server_url = web_server_url.rstrip('/')
        self.server = Server("searxng-mcp-client")
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools by fetching from web server."""
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(f"{self.web_server_url}/tools")
                    response.raise_for_status()
                    data = response.json()
                    
                    tools = []
                    for tool_data in data.get("tools", []):
                        tools.append(types.Tool(
                            name=tool_data["name"],
                            description=tool_data["description"],
                            inputSchema=tool_data["inputSchema"]
                        ))
                    
                    return tools
            except Exception as e:
                logger.error(f"Error fetching tools: {e}")
                return []

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any] | None
        ) -> List[types.TextContent]:
            """Handle tool calls by forwarding to web server."""
            if arguments is None:
                arguments = {}

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.web_server_url}/tools/{name}",
                        json=arguments
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    result = data.get("result", [])
                    if isinstance(result, list) and result:
                        return [types.TextContent(
                            type="text",
                            text=item.get("text", str(item))
                        ) for item in result]
                    else:
                        return [types.TextContent(
                            type="text",
                            text=str(result)
                        )]
                        
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    async def run(self):
        """Run the MCP client."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="searxng-mcp-client",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

async def main():
    """Main entry point."""
    # Get web server URL from environment or command line
    web_server_url = os.getenv("SEARXNG_MCP_WEB_URL")
    if not web_server_url and len(sys.argv) > 1:
        web_server_url = sys.argv[1]
    if not web_server_url:
        web_server_url = "https://your-mcp-app.railway.app"
    
    logger.info(f"Starting SearXNG MCP Client connecting to: {web_server_url}")
    
    client = SearXNGMCPClient(web_server_url)
    await client.run()

if __name__ == "__main__":
    asyncio.run(main()) 