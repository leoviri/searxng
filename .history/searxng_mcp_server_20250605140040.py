    #!/usr/bin/env python3
    """
    SearXNG MCP Server

    An MCP (Model Context Protocol) server that provides search functionality
    using a SearXNG instance as the backend with full API parameter support.
    """

    import asyncio
    import json
    import logging
    from typing import Any, Dict, List, Optional, Sequence, Union
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
                        description="Search the web using SearXNG metasearch engine with full customization options",
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
                                "engines": {
                                    "type": "string",
                                    "description": "Specific search engines to use (comma-separated). Leave empty for default engines.",
                                    "default": ""
                                },
                                "language": {
                                    "type": "string", 
                                    "description": "Search language (e.g., 'en', 'fr', 'de')",
                                    "default": "en"
                                },
                                "pageno": {
                                    "type": "integer",
                                    "description": "Search page number",
                                    "default": 1,
                                    "minimum": 1
                                },
                                "time_range": {
                                    "type": "string",
                                    "description": "Time range of search. Options: day, month, year",
                                    "enum": ["day", "month", "year"]
                                },
                                "safesearch": {
                                    "type": "integer",
                                    "description": "Filter search results. 0=off, 1=moderate, 2=strict",
                                    "enum": [0, 1, 2],
                                    "default": 0
                                },
                                "format": {
                                    "type": "string",
                                    "description": "Output format",
                                    "enum": ["json", "csv", "rss"],
                                    "default": "json"
                                },
                                "results_on_new_tab": {
                                    "type": "integer",
                                    "description": "Open search results on new tab. 0=no, 1=yes",
                                    "enum": [0, 1],
                                    "default": 0
                                },
                                "image_proxy": {
                                    "type": "boolean",
                                    "description": "Proxy image results through SearXNG"
                                },
                                "autocomplete": {
                                    "type": "string",
                                    "description": "Service which completes words as you type",
                                    "enum": ["google", "dbpedia", "duckduckgo", "mwmbl", "startpage", "wikipedia", "stract", "swisscows", "qwant"]
                                },
                                "theme": {
                                    "type": "string",
                                    "description": "Theme of the search interface",
                                    "default": "simple"
                                },
                                "enabled_plugins": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of enabled plugins. Options: Hash_plugin, Self_Information, Tracker_URL_remover, Ahmia_blacklist, Hostnames_plugin, Open_Access_DOI_rewrite, Vim-like_hotkeys, Tor_check_plugin"
                                },
                                "disabled_plugins": {
                                    "type": "array", 
                                    "items": {"type": "string"},
                                    "description": "List of disabled plugins"
                                },
                                "enabled_engines": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of enabled engines"
                                },
                                "disabled_engines": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of disabled engines"
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "Maximum number of results to return (internal limit, not sent to SearXNG)",
                                    "default": 10,
                                    "minimum": 1,
                                    "maximum": 100
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    types.Tool(
                        name="search_images",
                        description="Search for images using SearXNG with advanced options",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Image search query"
                                },
                                "engines": {
                                    "type": "string",
                                    "description": "Specific image search engines to use (comma-separated)"
                                },
                                "language": {
                                    "type": "string", 
                                    "description": "Search language",
                                    "default": "en"
                                },
                                "pageno": {
                                    "type": "integer",
                                    "description": "Page number",
                                    "default": 1,
                                    "minimum": 1
                                },
                                "time_range": {
                                    "type": "string",
                                    "description": "Time range. Options: day, month, year",
                                    "enum": ["day", "month", "year"]
                                },
                                "safesearch": {
                                    "type": "integer",
                                    "description": "Safe search filter. 0=off, 1=moderate, 2=strict",
                                    "enum": [0, 1, 2],
                                    "default": 0
                                },
                                "image_proxy": {
                                    "type": "boolean",
                                    "description": "Proxy image results through SearXNG"
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "Maximum number of image results to return",
                                    "default": 10,
                                    "minimum": 1,
                                    "maximum": 50
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    types.Tool(
                        name="search_news",
                        description="Search for news articles using SearXNG with advanced filtering",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "News search query"
                                },
                                "engines": {
                                    "type": "string",
                                    "description": "Specific news search engines to use (comma-separated)"
                                },
                                "language": {
                                    "type": "string", 
                                    "description": "Search language",
                                    "default": "en"
                                },
                                "pageno": {
                                    "type": "integer",
                                    "description": "Page number",
                                    "default": 1,
                                    "minimum": 1
                                },
                                "time_range": {
                                    "type": "string",
                                    "description": "Time range for news. Options: day, month, year",
                                    "enum": ["day", "month", "year"]
                                },
                                "safesearch": {
                                    "type": "integer",
                                    "description": "Safe search filter",
                                    "enum": [0, 1, 2],
                                    "default": 0
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "Maximum number of news results to return",
                                    "default": 10,
                                    "minimum": 1,
                                    "maximum": 50
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    types.Tool(
                        name="search_videos",
                        description="Search for videos using SearXNG",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Video search query"
                                },
                                "engines": {
                                    "type": "string",
                                    "description": "Specific video search engines to use (comma-separated)"
                                },
                                "language": {
                                    "type": "string", 
                                    "description": "Search language",
                                    "default": "en"
                                },
                                "pageno": {
                                    "type": "integer",
                                    "description": "Page number",
                                    "default": 1,
                                    "minimum": 1
                                },
                                "time_range": {
                                    "type": "string",
                                    "description": "Time range. Options: day, month, year",
                                    "enum": ["day", "month", "year"]
                                },
                                "safesearch": {
                                    "type": "integer",
                                    "description": "Safe search filter",
                                    "enum": [0, 1, 2],
                                    "default": 0
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "Maximum number of video results to return",
                                    "default": 10,
                                    "minimum": 1,
                                    "maximum": 30
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    types.Tool(
                        name="search_science",
                        description="Search for scientific articles and papers using SearXNG",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Scientific search query"
                                },
                                "engines": {
                                    "type": "string",
                                    "description": "Specific science search engines to use (comma-separated)"
                                },
                                "language": {
                                    "type": "string", 
                                    "description": "Search language",
                                    "default": "en"
                                },
                                "pageno": {
                                    "type": "integer",
                                    "description": "Page number",
                                    "default": 1,
                                    "minimum": 1
                                },
                                "time_range": {
                                    "type": "string",
                                    "description": "Time range. Options: day, month, year",
                                    "enum": ["day", "month", "year"]
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "Maximum number of results to return",
                                    "default": 10,
                                    "minimum": 1,
                                    "maximum": 30
                                }
                                                    },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="advanced_search",
                    description="Advanced search with explicit search operators and syntax support",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Advanced search query with operators (e.g., 'site:github.com python', '\"exact phrase\"', 'term1 OR term2')"
                            },
                            "site": {
                                "type": "string",
                                "description": "Limit search to specific site (will add site: operator)"
                            },
                            "filetype": {
                                "type": "string",
                                "description": "Search for specific file types (will add filetype: operator)"
                            },
                            "exclude_terms": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Terms to exclude from search (will add - operator)"
                            },
                            "exact_phrase": {
                                "type": "string",
                                "description": "Exact phrase to search for (will be quoted)"
                            },
                            "categories": {
                                "type": "string",
                                "description": "Search categories",
                                "default": "general"
                            },
                            "engines": {
                                "type": "string",
                                "description": "Specific search engines to use"
                            },
                            "language": {
                                "type": "string",
                                "description": "Search language",
                                "default": "en"
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Time range filter",
                                "enum": ["day", "month", "year"]
                            },
                            "safesearch": {
                                "type": "integer",
                                "description": "Safe search level",
                                "enum": [0, 1, 2],
                                "default": 0
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum results to return",
                                "default": 15,
                                "minimum": 1,
                                "maximum": 100
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
                    elif name == "search_videos":
                        return await self._search_videos(arguments)
                                    elif name == "search_science":
                    return await self._search_science(arguments)
                elif name == "advanced_search":
                    return await self._advanced_search(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                except Exception as e:
                    logger.error(f"Error in tool {name}: {e}")
                    return [types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}"
                    )]

            def _build_search_params(self, arguments: Dict[str, Any], default_categories: str = "general") -> Dict[str, Any]:
        """Build search parameters from arguments, supporting all SearXNG API parameters."""
        params = {
            "q": arguments.get("query", ""),
            "format": arguments.get("format", "json"),
            "categories": arguments.get("categories", default_categories),
            "language": arguments.get("language", "en")
        }
        
        # Optional parameters - only add if provided
        optional_params = [
            "engines", "pageno", "time_range", "safesearch", 
            "results_on_new_tab", "image_proxy", "autocomplete", "theme"
        ]
        
        for param in optional_params:
            if param in arguments and arguments[param] is not None:
                params[param] = arguments[param]
        
        # Handle array parameters
        array_params = ["enabled_plugins", "disabled_plugins", "enabled_engines", "disabled_engines"]
        for param in array_params:
            if param in arguments and arguments[param]:
                # Convert array to comma-separated string
                params[param] = ",".join(arguments[param])
        
        return params

        async def _search(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Perform a general web search with full parameter support."""
            max_results = arguments.get("max_results", 10)
            params = self._build_search_params(arguments, "general")
            
            return await self._perform_search(params, max_results, "Web Search")

        async def _search_images(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Perform an image search with advanced options."""
            max_results = arguments.get("max_results", 10)
            params = self._build_search_params(arguments, "images")
            
            return await self._perform_search(params, max_results, "Image Search")

        async def _search_news(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Perform a news search with filtering options."""
            max_results = arguments.get("max_results", 10)
            params = self._build_search_params(arguments, "news")
            
            return await self._perform_search(params, max_results, "News Search")

        async def _search_videos(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Perform a video search."""
            max_results = arguments.get("max_results", 10)
            params = self._build_search_params(arguments, "videos")
            
            return await self._perform_search(params, max_results, "Video Search")

            async def _search_science(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Perform a science/academic search."""
        max_results = arguments.get("max_results", 10)
        params = self._build_search_params(arguments, "science")
        
        return await self._perform_search(params, max_results, "Science Search")

    async def _advanced_search(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Perform an advanced search with enhanced query building."""
        max_results = arguments.get("max_results", 15)
        
        # Build enhanced query with search operators
        base_query = arguments.get("query", "")
        query_parts = [base_query] if base_query else []
        
        # Add site restriction
        if arguments.get("site"):
            query_parts.append(f"site:{arguments['site']}")
        
        # Add filetype restriction
        if arguments.get("filetype"):
            query_parts.append(f"filetype:{arguments['filetype']}")
        
        # Add exact phrase
        if arguments.get("exact_phrase"):
            query_parts.append(f'"{arguments["exact_phrase"]}"')
        
        # Add excluded terms
        if arguments.get("exclude_terms"):
            for term in arguments["exclude_terms"]:
                query_parts.append(f"-{term}")
        
        # Combine all query parts
        enhanced_query = " ".join(query_parts)
        
        # Build search parameters
        search_args = arguments.copy()
        search_args["query"] = enhanced_query
        params = self._build_search_params(search_args, arguments.get("categories", "general"))
        
        return await self._perform_search(params, max_results, "Advanced Search", use_post=True)

        async def _perform_search(self, params: Dict[str, Any], max_results: int, search_type: str, use_post: bool = False) -> List[types.TextContent]:
            """Perform the actual search request to SearXNG."""
            try:
                search_url = f"{self.searxng_url}/search"
                
                # Log the search parameters for debugging
                logger.info(f"Searching with params: {params}")
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(search_url, params=params)
                    response.raise_for_status()
                    
                    # Handle different response formats
                    content_type = response.headers.get("content-type", "").lower()
                    
                    if params.get("format") == "json" or "json" in content_type:
                        data = response.json()
                        results = data.get("results", [])
                        
                        if not results:
                            return [types.TextContent(
                                type="text",
                                text=f"No results found for query: {params['q']}"
                            )]
                        
                        # Limit results
                        results = results[:max_results]
                        
                        # Format results with additional metadata
                        formatted_results = self._format_results(results, search_type, params['q'], data)
                        
                        return [types.TextContent(
                            type="text",
                            text=formatted_results
                        )]
                    
                    elif params.get("format") == "csv":
                        return [types.TextContent(
                            type="text",
                            text=f"# {search_type} Results (CSV format)\n\n{response.text}"
                        )]
                    
                    elif params.get("format") == "rss":
                        return [types.TextContent(
                            type="text",
                            text=f"# {search_type} Results (RSS format)\n\n{response.text}"
                        )]
                    
                    else:
                        return [types.TextContent(
                            type="text",
                            text=f"# {search_type} Results\n\n{response.text}"
                        )]
                    
            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error connecting to SearXNG: {str(e)}"
                )]
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error parsing response from SearXNG: {str(e)}"
                )]
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Unexpected error: {str(e)}"
                )]

        def _format_results(self, results: List[Dict[str, Any]], search_type: str, query: str, metadata: Dict[str, Any] = None) -> str:
            """Format search results for display with enhanced information."""
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
                
                # Clean up content
                if content:
                    content = content.strip()
                    if len(content) > 300:
                        content = content[:300] + "..."
                
                output.append(f"## {i}. {title}")
                output.append(f"**URL:** {url}")
                
                if content:
                    output.append(f"**Summary:** {content}")
                
                # Add extra info for specific result types
                if "publishedDate" in result and result["publishedDate"]:
                    output.append(f"**Published:** {result['publishedDate']}")
                
                if "thumbnail" in result and result["thumbnail"]:
                    output.append(f"**Thumbnail:** {result['thumbnail']}")
                
                # Video-specific fields
                if "duration" in result and result["duration"]:
                    output.append(f"**Duration:** {result['duration']}")
                
                # Image-specific fields  
                if "img_src" in result and result["img_src"]:
                    output.append(f"**Image URL:** {result['img_src']}")
                
                if "img_format" in result and result["img_format"]:
                    output.append(f"**Format:** {result['img_format']}")
                
                # Scientific paper fields
                if "doi" in result and result["doi"]:
                    output.append(f"**DOI:** {result['doi']}")
                
                if "authors" in result and result["authors"]:
                    output.append(f"**Authors:** {', '.join(result['authors']) if isinstance(result['authors'], list) else result['authors']}")
                
                # Engine information
                if "engine" in result:
                    output.append(f"**Source Engine:** {result['engine']}")
                
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
                        server_version="2.0.0",
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
        
        logger.info(f"Starting Enhanced SearXNG MCP Server v2.0.0 with backend: {searxng_url}")
        logger.info("Supported search types: general, images, news, videos, science")
        logger.info("Full SearXNG API parameter support enabled")
        
        server = SearXNGMCPServer(searxng_url)
        await server.run()

    if __name__ == "__main__":
        asyncio.run(main()) 