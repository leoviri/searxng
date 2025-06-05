#!/usr/bin/env python3
"""
SearXNG MCP Server

An MCP (Model Context Protocol) server that provides search functionality
using a local SearXNG instance as the backend.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import quote_plus, urlencode

import httpx
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("searxng-mcp")

class SearXNGMCPServer:
    def __init__(self, searxng_url: str = "http://localhost:8080"):
        self.searxng_url = searxng_url
        self.server = Server("searxng-mcp")
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="search",
                    description="Search the web using SearXNG metasearch engine",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "categories": {
                                "type": "string",
                                "description": "Search categories (comma-separated). Options: general, images, videos, news, music, files, it, science, social media",
                                "default": "general"
                            },
                            "language": {
                                "type": "string", 
                                "description": "Search language (e.g., 'en', 'fr', 'de')",
                                "default": "en"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50
                            },
                            "engines": {
                                "type": "string",
                                "description": "Specific search engines to use (comma-separated). Leave empty for default engines.",
                                "default": ""
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="search_images",
                    description="Search for images using SearXNG",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Image search query"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of image results to return",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 30
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="search_news",
                    description="Search for news articles using SearXNG",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "News search query"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of news results to return",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 30
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any] | None
        ) -> List[types.TextContent]:
            """Handle tool calls."""
            if arguments is None:
                arguments = {}

            try:
                if name == "search":
                    return await self._search(arguments)
                elif name == "search_images":
                    return await self._search_images(arguments)
                elif name == "search_news":
                    return await self._search_news(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    async def _search(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Perform a general web search."""
        query = arguments.get("query", "")
        categories = arguments.get("categories", "general")
        language = arguments.get("language", "en")
        max_results = arguments.get("max_results", 10)
        engines = arguments.get("engines", "")

        params = {
            "q": query,
            "format": "json",
            "categories": categories,
            "language": language
        }
        
        if engines:
            params["engines"] = engines

        return await self._perform_search(params, max_results, "Web Search")

    async def _search_images(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Perform an image search."""
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 10)

        params = {
            "q": query,
            "format": "json",
            "categories": "images"
        }

        return await self._perform_search(params, max_results, "Image Search")

    async def _search_news(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Perform a news search."""
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 10)

        params = {
            "q": query,
            "format": "json",
            "categories": "news"
        }

        return await self._perform_search(params, max_results, "News Search")

    async def _perform_search(self, params: Dict[str, Any], max_results: int, search_type: str) -> List[types.TextContent]:
        """Perform the actual search request to SearXNG."""
        try:
            search_url = f"{self.searxng_url}/search"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(search_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    return [types.TextContent(
                        type="text",
                        text=f"No results found for query: {params['q']}"
                    )]
                
                # Limit results
                results = results[:max_results]
                
                # Format results
                formatted_results = self._format_results(results, search_type, params['q'])
                
                return [types.TextContent(
                    type="text",
                    text=formatted_results
                )]
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error connecting to SearXNG: {str(e)}"
            )]
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return [types.TextContent(
                type="text",
                text=f"Unexpected error: {str(e)}"
            )]

    def _format_results(self, results: List[Dict[str, Any]], search_type: str, query: str) -> str:
        """Format search results for display."""
        output = [f"# {search_type} Results for: {query}\n"]
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            content = result.get("content", "")
            
            # Clean up content
            if content:
                content = content.strip()
                if len(content) > 200:
                    content = content[:200] + "..."
            
            output.append(f"## {i}. {title}")
            output.append(f"**URL:** {url}")
            
            if content:
                output.append(f"**Summary:** {content}")
            
            # Add extra info for specific result types
            if "publishedDate" in result and result["publishedDate"]:
                output.append(f"**Published:** {result['publishedDate']}")
            
            if "thumbnail" in result and result["thumbnail"]:
                output.append(f"**Thumbnail:** {result['thumbnail']}")
            
            output.append("")  # Empty line between results
        
        return "\n".join(output)

    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="searxng-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

async def main():
    """Main entry point."""
    import sys
    import os
    
    # Use environment variable first, then command line arg, then default
    searxng_url = os.getenv("SEARXNG_URL")
    if not searxng_url and len(sys.argv) > 1:
        searxng_url = sys.argv[1]
    if not searxng_url:
        searxng_url = "http://localhost:8080"
    
    logger.info(f"Starting SearXNG MCP Server with backend: {searxng_url}")
    
    server = SearXNGMCPServer(searxng_url)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main()) 