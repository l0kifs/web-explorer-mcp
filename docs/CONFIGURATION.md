# Configuration Guide

Complete configuration reference for Web Explorer MCP.

## AI Client Configuration

### Claude Desktop

Add the following to your Claude Desktop configuration file:

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration:**

```json
{
  "mcpServers": {
    "web-explorer": {
      "command": "uvx",
      "args": ["web-explorer-mcp"]
    }
  }
}
```

Or if you're using uv with a local installation:

```json
{
  "mcpServers": {
    "web-explorer": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/web-explorer-mcp",
        "run",
        "web-explorer-mcp"
      ]
    }
  }
}
```

### Continue.dev

Add to your `~/.continue/config.json`:

```json
{
  "mcpServers": [
    {
      "name": "web-explorer",
      "command": "uvx",
      "args": ["web-explorer-mcp"]
    }
  ]
}
```

### Cline (VS Code Extension)

Add to your Cline MCP settings:

```json
{
  "web-explorer": {
    "command": "uvx",
    "args": ["web-explorer-mcp"]
  }
}
```

## Environment Variables

You can customize the MCP server behavior using environment variables:

```bash
# SearxNG URL (default: http://127.0.0.1:9011)
export WEB_EXPLORER_MCP_WEB_SEARCH_SEARXNG_URL="http://localhost:9011"

# Default page size for search results (default: 5)
export WEB_EXPLORER_MCP_WEB_SEARCH_DEFAULT_PAGE_SIZE=10

# Request timeout in seconds (default: 15)
export WEB_EXPLORER_MCP_WEB_SEARCH_TIMEOUT=20

# Maximum characters for webpage content (default: 5000)
export WEB_EXPLORER_MCP_WEBPAGE_MAX_CHARS=10000

# Playwright remote server URL (default: http://127.0.0.1:9012)
export WEB_EXPLORER_MCP_PLAYWRIGHT_CONNECTION_URL="http://localhost:9012"

# Playwright timeout in seconds (default: 30)
export WEB_EXPLORER_MCP_PLAYWRIGHT_TIMEOUT=30

# Enable debug mode (default: false)
export WEB_EXPLORER_MCP_DEBUG=true
```

### Using Environment Variables with Claude Desktop

```json
{
  "mcpServers": {
    "web-explorer": {
      "command": "uvx",
      "args": ["web-explorer-mcp"],
      "env": {
        "WEB_EXPLORER_MCP_WEB_SEARCH_DEFAULT_PAGE_SIZE": "10",
        "WEB_EXPLORER_MCP_WEBPAGE_MAX_CHARS": "8000"
      }
    }
  }
}
```

## Tools Reference

### `web_search_tool`
- **query** (required) - Search query
- **page** (optional, default: 1) - Page number
- **page_size** (optional, default: 5) - Results per page

### `webpage_content_tool`
- **url** (required) - URL to extract
- **max_chars** (optional, default: 5000) - Max characters

## Management

**Docker Services (SearxNG + Playwright):**
```bash
docker compose logs -f searxng    # View SearxNG logs
docker compose logs -f playwright # View Playwright logs
docker compose restart searxng    # Restart SearxNG
docker compose restart playwright # Restart Playwright
docker compose up -d              # Start all services
docker compose down               # Stop all services
docker compose pull && docker compose up -d  # Update all services
```

**MCP Server:**
```bash
uvx --force web-explorer-mcp  # Update
```

## Troubleshooting

**Docker not running:**
```bash
sudo systemctl start docker  # Linux
# Or start Docker Desktop
```

**Port 9011 or 9012 in use:**
Change port in `docker-compose.yml` and update corresponding env vars:
- `WEB_EXPLORER_MCP_WEB_SEARCH_SEARXNG_URL` for SearxNG
- `WEB_EXPLORER_MCP_PLAYWRIGHT_CONNECTION_URL` for Playwright

**Services not accessible:**
```bash
docker compose ps                  # Check status
docker compose logs searxng        # Check SearxNG logs
docker compose logs playwright     # Check Playwright logs
curl http://localhost:9011         # Test SearxNG
curl http://localhost:9012         # Test Playwright
```

**Claude doesn't see tools:**
1. Save config file
2. Completely quit and restart Claude
3. Check Claude's logs

**Permission denied:**
```bash
chmod +x install.sh
```
