# Contributing

## Setup

```bash
git clone https://github.com/l0kifs/web-explorer-mcp.git
cd web-explorer-mcp
uv sync
docker compose up -d
uv run web-explorer-mcp
```

## Development

```bash
uv run ruff check .      # Lint
uv run ruff format .     # Format
uv run pytest            # Test
```

## Pull Request

1. Create branch: `git checkout -b feature/name`
2. Make changes
3. Test: `uv run pytest`
4. Commit: `git commit -m "feat: description"` (use [Conventional Commits](https://www.conventionalcommits.org/))
5. Push and create PR

## Adding Tools

1. Add integration in `src/web_explorer_mcp/integrations/`
2. Register in `src/web_explorer_mcp/entrypoints/mcp/server.py`
3. Add tests in `tests/`
4. Update docs

Example:
```python
@mcp.tool()
def new_tool(param: str) -> dict:
    """Tool description for LLM."""
    pass
```

## Project Structure

```
src/web_explorer_mcp/
├── config/       # Settings
├── entrypoints/  # MCP server
└── integrations/ # Tools
```

## License

MIT - By contributing, you agree to license under MIT.
