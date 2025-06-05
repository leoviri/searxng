#!/usr/bin/env python3
"""
SearXNG MCP Web Server

A web-based version of the MCP server that can be deployed to Railway
and accessed via HTTP instead of stdio.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urlencode

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("searxng-mcp-web")

app = FastAPI(title="SearXNG MCP Web Server", version="1.0.0")

class SearXNGSearcher:
    def __init__(self, searxng_url: str = "http://localhost:8080"):
        self.searxng_url = searxng_url

    async def search(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
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

    async def search_images(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform an image search."""
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 10)

        params = {
            "q": query,
            "format": "json",
            "categories": "images"
        }

        return await self._perform_search(params, max_results, "Image Search")

    async def search_news(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform a news search."""
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 10)

        params = {
            "q": query,
            "format": "json",
            "categories": "news"
        }

        return await self._perform_search(params, max_results, "News Search")

    async def _perform_search(self, params: Dict[str, Any], max_results: int, search_type: str) -> List[Dict[str, Any]]:
        """Perform the actual search request to SearXNG."""
        try:
            search_url = f"{self.searxng_url}/search"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(search_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    return [{
                        "type": "text",
                        "text": f"No results found for query: {params['q']}"
                    }]
                
                # Limit results
                results = results[:max_results]
                
                # Format results
                formatted_results = self._format_results(results, search_type, params['q'])
                
                return [{
                    "type": "text",
                    "text": formatted_results
                }]
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return [{
                "type": "text",
                "text": f"Error connecting to SearXNG: {str(e)}"
            }]
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return [{
                "type": "text",
                "text": f"Unexpected error: {str(e)}"
            }]

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

# Initialize searcher
searxng_url = os.getenv("SEARXNG_URL", "http://localhost:8080")
searcher = SearXNGSearcher(searxng_url)

@app.get("/")
async def root():
    return {"message": "SearXNG MCP Web Server", "version": "1.0.0"}

@app.get("/tools")
async def list_tools():
    """List available tools."""
    return {
        "tools": [
            {
                "name": "search",
                "description": "Search the web using SearXNG metasearch engine",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "categories": {"type": "string", "description": "Search categories", "default": "general"},
                        "language": {"type": "string", "description": "Search language", "default": "en"},
                        "max_results": {"type": "integer", "description": "Maximum results", "default": 10},
                        "engines": {"type": "string", "description": "Specific engines", "default": ""}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "search_images",
                "description": "Search for images using SearXNG",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Image search query"},
                        "max_results": {"type": "integer", "description": "Maximum results", "default": 10}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "search_news",
                "description": "Search for news using SearXNG",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "News search query"},
                        "max_results": {"type": "integer", "description": "Maximum results", "default": 10}
                    },
                    "required": ["query"]
                }
            }
        ]
    }

@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, arguments: Dict[str, Any]):
    """Call a specific tool."""
    try:
        if tool_name == "search":
            result = await searcher.search(arguments)
        elif tool_name == "search_images":
            result = await searcher.search_images(arguments)
        elif tool_name == "search_news":
            result = await searcher.search_news(arguments)
        else:
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
        
        return {"result": result}
    except Exception as e:
        logger.error(f"Error in tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 