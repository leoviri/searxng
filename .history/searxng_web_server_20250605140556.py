#!/usr/bin/env python3
"""
SearXNG Web API Server

A FastAPI web server that exposes SearXNG MCP functionality via HTTP endpoints.
This can be deployed to Railway, Heroku, or any cloud platform.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("searxng-web-server")

app = FastAPI(
    title="SearXNG MCP Web API",
    description="Web API for SearXNG metasearch functionality",
    version="2.1.0"
)

# Enable CORS for web usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get SearXNG URL from environment
SEARXNG_URL = os.getenv("SEARXNG_URL", "https://searx.be")

class ToolRequest(BaseModel):
    query: str
    categories: Optional[str] = "general"
    engines: Optional[str] = ""
    language: Optional[str] = "en"
    pageno: Optional[int] = 1
    time_range: Optional[str] = None
    safesearch: Optional[int] = 0
    format: Optional[str] = "json"
    results_on_new_tab: Optional[int] = 0
    image_proxy: Optional[bool] = None
    autocomplete: Optional[str] = None
    theme: Optional[str] = "simple"
    enabled_plugins: Optional[List[str]] = None
    disabled_plugins: Optional[List[str]] = None
    enabled_engines: Optional[List[str]] = None
    disabled_engines: Optional[List[str]] = None
    max_results: Optional[int] = 10
    
class AdvancedSearchRequest(BaseModel):
    query: str
    site: Optional[str] = None
    filetype: Optional[str] = None
    exclude_terms: Optional[List[str]] = None
    exact_phrase: Optional[str] = None
    categories: Optional[str] = "general"
    engines: Optional[str] = ""
    language: Optional[str] = "en"
    time_range: Optional[str] = None
    safesearch: Optional[int] = 0
    max_results: Optional[int] = 15

class ToolResponse(BaseModel):
    result: List[Dict[str, str]]

class SearXNGWebAPI:
    def __init__(self, searxng_url: str):
        self.searxng_url = searxng_url

    def _build_search_params(self, request_data: Dict[str, Any], default_categories: str = "general") -> Dict[str, Any]:
        """Build search parameters from request data."""
        params = {
            "q": request_data.get("query", ""),
            "format": request_data.get("format", "json"),
            "categories": request_data.get("categories", default_categories),
            "language": request_data.get("language", "en")
        }
        
        # Optional parameters
        optional_params = [
            "engines", "pageno", "time_range", "safesearch", 
            "results_on_new_tab", "image_proxy", "autocomplete", "theme"
        ]
        
        for param in optional_params:
            if param in request_data and request_data[param] is not None:
                params[param] = request_data[param]
        
        # Handle array parameters
        array_params = ["enabled_plugins", "disabled_plugins", "enabled_engines", "disabled_engines"]
        for param in array_params:
            if param in request_data and request_data[param]:
                params[param] = ",".join(request_data[param])
        
        return params

    def _build_advanced_query(self, request: AdvancedSearchRequest) -> str:
        """Build advanced search query with operators."""
        query_parts = [request.query] if request.query else []
        
        if request.site:
            query_parts.append(f"site:{request.site}")
        
        if request.filetype:
            query_parts.append(f"filetype:{request.filetype}")
        
        if request.exact_phrase:
            query_parts.append(f'"{request.exact_phrase}"')
        
        if request.exclude_terms:
            for term in request.exclude_terms:
                query_parts.append(f"-{term}")
        
        return " ".join(query_parts)

    async def _perform_search(self, params: Dict[str, Any], max_results: int, search_type: str, use_post: bool = False) -> Dict[str, Any]:
        """Perform search request to SearXNG."""
        try:
            search_url = f"{self.searxng_url}/search"
            
            logger.info(f"Searching with params: {params} (method: {'POST' if use_post else 'GET'})")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                if use_post:
                    response = await client.post(search_url, data=params)
                else:
                    response = await client.get(search_url, params=params)
                response.raise_for_status()
                
                content_type = response.headers.get("content-type", "").lower()
                
                if params.get("format") == "json" or "json" in content_type:
                    data = response.json()
                    results = data.get("results", [])
                    
                    if not results:
                        return {
                            "results": [],
                            "message": f"No results found for query: {params['q']}",
                            "metadata": data
                        }
                    
                    # Limit results
                    results = results[:max_results]
                    
                    # Format results
                    formatted_results = self._format_results(results, search_type, params['q'], data)
                    
                    return {
                        "results": [{"text": formatted_results}],
                        "metadata": data,
                        "total_results": len(results)
                    }
                else:
                    return {
                        "results": [{"text": f"# {search_type} Results\n\n{response.text}"}],
                        "format": params.get("format", "unknown")
                    }
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise HTTPException(status_code=503, detail=f"Error connecting to SearXNG: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise HTTPException(status_code=502, detail=f"Error parsing response from SearXNG: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    def _format_results(self, results: List[Dict[str, Any]], search_type: str, query: str, metadata: Dict[str, Any] = None) -> str:
        """Format search results for display."""
        output = [f"# {search_type} Results for: {query}\n"]
        
        # Add metadata if available
        if metadata:
            if "number_of_results" in metadata:
                output.append(f"**Total Results Found:** {metadata['number_of_results']}")
            if "query" in metadata and metadata["query"] != query:
                output.append(f"**Processed Query:** {metadata['query']}")
            if "engines" in metadata:
                output.append(f"**Search Engines Used:** {', '.join(metadata['engines'])}")
            output.append("")
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            content = result.get("content", "")
            
            if content:
                content = content.strip()
                if len(content) > 300:
                    content = content[:300] + "..."
            
            output.append(f"## {i}. {title}")
            output.append(f"**URL:** {url}")
            
            if content:
                output.append(f"**Summary:** {content}")
            
            # Add extra fields based on content type
            extra_fields = ["publishedDate", "thumbnail", "duration", "img_src", "img_format", "doi", "authors", "engine"]
            for field in extra_fields:
                if field in result and result[field]:
                    if field == "authors" and isinstance(result[field], list):
                        output.append(f"**{field.title()}:** {', '.join(result[field])}")
                    else:
                        output.append(f"**{field.title()}:** {result[field]}")
            
            output.append("")
        
        return "\n".join(output)

# Initialize the API
searxng_api = SearXNGWebAPI(SEARXNG_URL)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "SearXNG MCP Web API",
        "version": "2.1.0",
        "description": "Web API for SearXNG metasearch functionality",
        "searxng_backend": SEARXNG_URL,
        "endpoints": {
            "tools": "/tools",
            "search": "/tools/search",
            "search_images": "/tools/search_images",
            "search_news": "/tools/search_news",
            "search_videos": "/tools/search_videos",
            "search_science": "/tools/search_science",
            "advanced_search": "/tools/advanced_search"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{SEARXNG_URL}/")
            return {
                "status": "healthy",
                "searxng_backend": SEARXNG_URL,
                "searxng_status": response.status_code
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "searxng_backend": SEARXNG_URL,
            "error": str(e)
        }

@app.get("/tools")
async def list_tools():
    """List available search tools."""
    tools = [
        {
            "name": "search",
            "description": "Search the web using SearXNG metasearch engine with full customization options",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "categories": {"type": "string", "description": "Search categories", "default": "general"},
                    "engines": {"type": "string", "description": "Specific engines to use"},
                    "language": {"type": "string", "description": "Search language", "default": "en"},
                    "max_results": {"type": "integer", "description": "Maximum results", "default": 10}
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
        },
        {
            "name": "search_videos",
            "description": "Search for videos using SearXNG",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Video search query"},
                    "max_results": {"type": "integer", "description": "Maximum results", "default": 10}
                },
                "required": ["query"]
            }
        },
        {
            "name": "search_science",
            "description": "Search for scientific papers using SearXNG",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Scientific search query"},
                    "max_results": {"type": "integer", "description": "Maximum results", "default": 10}
                },
                "required": ["query"]
            }
        },
        {
            "name": "advanced_search",
            "description": "Advanced search with search operators",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "site": {"type": "string", "description": "Limit to specific site"},
                    "filetype": {"type": "string", "description": "Search for specific file types"},
                    "max_results": {"type": "integer", "description": "Maximum results", "default": 15}
                },
                "required": ["query"]
            }
        }
    ]
    return {"tools": tools}

@app.post("/tools/search")
async def search(request: ToolRequest):
    """General web search."""
    params = searxng_api._build_search_params(request.dict(), "general")
    result = await searxng_api._perform_search(params, request.max_results, "Web Search")
    return ToolResponse(result=result["results"])

@app.post("/tools/search_images")
async def search_images(request: ToolRequest):
    """Image search."""
    params = searxng_api._build_search_params(request.dict(), "images")
    result = await searxng_api._perform_search(params, request.max_results, "Image Search")
    return ToolResponse(result=result["results"])

@app.post("/tools/search_news")
async def search_news(request: ToolRequest):
    """News search."""
    params = searxng_api._build_search_params(request.dict(), "news")
    result = await searxng_api._perform_search(params, request.max_results, "News Search")
    return ToolResponse(result=result["results"])

@app.post("/tools/search_videos")
async def search_videos(request: ToolRequest):
    """Video search."""
    params = searxng_api._build_search_params(request.dict(), "videos")
    result = await searxng_api._perform_search(params, request.max_results, "Video Search")
    return ToolResponse(result=result["results"])

@app.post("/tools/search_science")
async def search_science(request: ToolRequest):
    """Science search."""
    params = searxng_api._build_search_params(request.dict(), "science")
    result = await searxng_api._perform_search(params, request.max_results, "Science Search")
    return ToolResponse(result=result["results"])

@app.post("/tools/advanced_search")
async def advanced_search(request: AdvancedSearchRequest):
    """Advanced search with operators."""
    enhanced_query = searxng_api._build_advanced_query(request)
    
    search_params = {
        "query": enhanced_query,
        "categories": request.categories,
        "engines": request.engines,
        "language": request.language,
        "time_range": request.time_range,
        "safesearch": request.safesearch
    }
    
    params = searxng_api._build_search_params(search_params, request.categories)
    result = await searxng_api._perform_search(params, request.max_results, "Advanced Search", use_post=True)
    return ToolResponse(result=result["results"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 