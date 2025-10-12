# Web Explorer MCP

A Model Context Protocol (MCP) server that provides web search and webpage content extraction using a local SearxNG instance.

## Why Web Explorer MCP?

Unlike commercial solutions (GitHub Copilot, Cursor IDE), Web Explorer MCP prioritizes **privacy** and **autonomy**:

| Feature          | Web Explorer MCP               | GitHub Copilot                 | Cursor IDE                          |
| ---------------- | ------------------------------ | ------------------------------ | ----------------------------------- |
| **Privacy**      | ✅ Local SearxNG, zero tracking | ❌ Bing API, Microsoft servers  | ❌ Cloud search, third-party APIs    |
| **Cost**         | ✅ Free, no limits              | 💰 $10-20/month subscription    | 💰 $20/month Pro plan                |
| **API Keys**     | ✅ None required                | ⚠️ GitHub account required      | ⚠️ Account & subscription            |
| **Data Control** | ✅ All data stays local         | ❌ Queries sent to Microsoft    | ❌ Queries sent to external services |
| **Setup**        | ✅ 2 commands                   | ⚠️ Account setup, policy config | ⚠️ Account, payment setup            |
| **Open Source**  | ✅ Fully auditable              | ⚠️ Partial (client only)        | ❌ Proprietary                       |

**Perfect for:** Developers who value privacy, work with sensitive data, or prefer not to depend on external services and subscriptions.

## Features

- 🔍 **Web Search** - Search using local SearxNG (private, no API keys)
- 📄 **Content Extraction** - Extract clean text from webpages with Playwright rendering
- 🐳 **Zero Pollution** - Runs in Docker, leaves no traces
- 🚀 **Simple Setup** - Install in 2 commands

## Quick Start

### 1. Install Services (SearxNG + Playwright)

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
- **`webpage_content_tool(url, max_chars, page)`** - Extract webpage content with pagination support

## Configuration & Usage

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for:
- Other AI clients (Continue.dev, Cline)
- Environment variables
- Troubleshooting
- Management commands

## Update

```bash
uvx --force web-explorer-mcp  # MCP server
docker compose pull && docker compose up -d  # SearxNG + Playwright
```

## Uninstall

```bash
docker compose down -v
cd .. && rm -rf web-explorer-mcp
```

## Development

```bash
uv sync              # Install dependencies
docker compose up -d # Start SearxNG + Playwright
uv run web-explorer-mcp  # Run locally
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT - see [LICENSE](LICENSE)