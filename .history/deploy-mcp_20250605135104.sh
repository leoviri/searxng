#!/bin/bash

# Install dependencies
pip install --no-cache-dir -r requirements-web.txt

# Run the MCP web server
python searxng_mcp_web_server.py 