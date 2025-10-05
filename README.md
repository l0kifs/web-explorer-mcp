# Web Explorer MCP

A Model Context Protocol (MCP) server that provides web search and webpage content extraction using a local SearxNG instance.

## Features

- 🔍 **Web Search** - Search using local SearxNG (private, no API keys)
- 📄 **Content Extraction** - Extract clean text from webpages
- 🐳 **Zero Pollution** - Runs in Docker, leaves no traces
- � **Simple Setup** - Install in 2 commands

## Quick Start

### 1. Install SearxNG

```bash
git clone https://github.com/l0kifs/web-explorer-mcp.git
cd web-explorer-mcp
./install.sh  # or ./install.fish for Fish shell
```

### 2. Configure Claude Desktop

Add to your Claude config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

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

### 3. Restart Claude

That's it! Ask Claude to search the web.

## Tools

- **`web_search_tool(query, page, page_size)`** - Search the web
- **`webpage_content_tool(url, max_chars)`** - Extract webpage content

## Configuration & Usage

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for:
- Other AI clients (Continue.dev, Cline)
- Environment variables
- Troubleshooting
- Management commands

## Update

```bash
uvx --force web-explorer-mcp  # MCP server
docker compose pull && docker compose up -d  # SearxNG
```

## Uninstall

```bash
docker compose down -v
cd .. && rm -rf web-explorer-mcp
```

## Development

```bash
uv sync              # Install dependencies
docker compose up -d # Start SearxNG
uv run web-explorer-mcp  # Run locally
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT

MIT - see [LICENSE](LICENSE)