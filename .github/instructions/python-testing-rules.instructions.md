---
applyTo: '**'
---
# Rules for an AI Agent Testing a Python Project (pytest)

Mandatory rules for writing and running tests. Primary framework: pytest.

## Basic principles
- Use pytest. Entry points: `tests/` directory; files `test_*.py`; functions `test_*`, classes `Test*` without `__init__`.
- Tests are isolated and deterministic: no external network, real databases, or clocks; side effects only via fixtures.
- Fast and minimal: one behavior per test; eliminate duplication via parametrization and fixtures.
- Clear names: `test_<unit>_<condition>_<expectation>`; assertion messages explain the reason.

## pytest practices (minimal yet sufficient)
- Fixtures
  - Use `@pytest.fixture` for setup/teardown; minimal `scope` (default `function`).
  - Use `tmp_path`/`monkeypatch`/`capsys`/`caplog` instead of manual mocks of environment/files/IO.
  - Avoid `autouse=True` except for truly global and safe setup.
- Parametrization
  - Use `@pytest.mark.parametrize(..., ids=...)` to cover variants instead of copy-paste.
  - Keep test data compact (tables, factories), not in long if-chains.
- Markers and stability
  - Use `@pytest.mark.skipif(...)` and `@pytest.mark.xfail(reason=..., strict=True)` for platform-specific/known cases.
  - Register custom markers (e.g., `slow`, `integration`) and mark long-running tests.
- Asynchrony
  - For async functions — `@pytest.mark.asyncio`. Isolate the event loop; don't mix sync/async in a single test.
- Asserts
  - Use built-in `assert`; for floats — `pytest.approx`.

## Quality and coverage
- Run with code coverage (pytest-cov/coverage.py). Goal — a realistic, maintainable minimum for the project; don't chase 100%.
- Mandatory reports: overall %, per-file coverage, branch misses.
- Cover critical paths first; exclude tests themselves and generated code from the report.
- Minimum thresholds (CI): overall line coverage ≥ 85%; for new/changed code, aim for ≥ 90%.

## Isolation and external effects
- FS: only via `tmp_path`. Network: mock/fake layers (e.g., adapter/factory); do not call real services.
- Time/UUID/environment: fix via fixtures/mocks (`monkeypatch`). Reset global state after the test.

## Test levels: requirements
- Unit (`-m "not integration and not e2e"` by default)
  - Isolation: no network/DB/FS; all external dependencies mocked (`monkeypatch`, test doubles).
  - Speed: < 100ms per test; always run.
  - Data: minimal inline fixtures, factories; prefer pure functions.
  - Reliability: deterministic, no randomness (fix seed/time).
- Integration (`@pytest.mark.integration`)
  - Purpose: verify interaction of multiple modules/layers (adapters, ORM, serialization).
  - Environment: local/ephemeral resources via fixtures (e.g., temporary DB, filesystem).
  - Stability: no external services; use fakes/containers; pre/post conditions are cleaned up.
  - Execution: in CI on changes at layer boundaries and on schedule.
- E2E (`@pytest.mark.e2e`)
  - Purpose: end-to-end user scenarios through the full stack.
  - Environment: controlled (docker-compose/ephemeral env); data initialized uniquely and cleaned up.
  - Requirements: reasonable timeouts, collect logs/artifacts on failures, minimize flakes.
  - Execution: separate from unit; less frequent.

## Minimal configuration (example)
Adjust for the project by filling in the package name and aligning markers.

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "-q -ra --strict-markers"
testpaths = ["tests"]
markers = [
  "unit: unit tests (by default without a marker)",
  "slow: long-running tests",
  "integration: integration tests",
  "e2e: end-to-end tests",
]

[tool.coverage.run]
branch = true
source = ["<top-level-package-name>"]
omit = ["tests/*", "**/__init__.py"]

[tool.coverage.report]
show_missing = true
skip_covered = true
fail_under = 85
```

## Run commands (local)
- Basic run: `uv run pytest`
- With coverage: `uv run pytest --cov --cov-report=term-missing`
- Only fast: `uv run pytest -m "not slow"`
- Integration only: `uv run pytest -m integration`
- E2E only: `uv run pytest -m e2e`

## Test acceptance criteria
- Tests pass locally and in CI; no flaky tests (flakes) without `xfail(strict=True)`.
- New logic is covered by tests; regressions are reproduced by a test before the fix.
- Pytest/coverage config is up to date; markers are registered; tests are fast and isolated.
- By levels: Unit — required for every change; Integration — for changes at module boundaries; E2E — for changes in business flows/in the release cycle.

## Code quality tools configuration

### Ruff (Linter and Formatter)
Ruff is an extremely fast Python linter and code formatter written in Rust. It replaces tools like flake8, isort, black, and more.

**Minimal configuration (pyproject.toml):**
```toml
[tool.ruff]
# Set the maximum line length to 88 (Black-compatible).
line-length = 88

# Assume Python 3.10+
target-version = "py310"

[tool.ruff.lint]
# Enable pycodestyle (E, W), Pyflakes (F), isort (I), flake8-bugbear (B)
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # Pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "UP",   # pyupgrade
    "SIM",  # flake8-simplify
]

# Avoid enforcing line-length violations (handled by formatter)
ignore = ["E501"]

[tool.ruff.format]
# Use double quotes for strings
quote-style = "double"

# Indent with spaces
indent-style = "space"

[tool.ruff.lint.pydocstyle]
# Use Google-style docstrings
convention = "google"
```

**Run commands:**
- Check code: `uv run ruff check`
- Fix issues automatically: `uv run ruff check --fix`
- Format code: `uv run ruff format`
- Check and format: `uv run ruff check --fix && uv run ruff format`

### Ty (Type Checker)
Ty is an extremely fast Python type checker and language server written in Rust, designed as a modern alternative to mypy and pyright.

**Minimal configuration (pyproject.toml):**
```toml
[tool.ty.environment]
# Specify Python version for type checking
python-version = "3.10"

# Path to Python environment (usually virtual environment)
python = "./.venv"

# Project root directories (auto-detected by default)
root = ["./src"]

# Platform target (optional: "linux", "darwin", "win32", "all")
python-platform = "linux"

[tool.ty.rules]
# Configure rule severity levels: "ignore", "warn", "error"
possibly-unresolved-reference = "warn"
invalid-assignment = "error"
index-out-of-bounds = "warn"
division-by-zero = "warn"

[tool.ty.src]
# Files and directories to type check
include = [
    "src",
    "tests",
]

# Files and directories to exclude from type checking
exclude = [
    "tests/fixtures/**",
    "**/*.proto",
    "generated/**",
]

# Override rules for specific files/directories
[[tool.ty.overrides]]
include = ["tests/**"]

[tool.ty.overrides.rules]
possibly-unresolved-reference = "ignore"
```

**Run commands:**
- Type check all files: `uv run ty check`
- Check specific file: `uv run ty check path/to/file.py`
- Use with uvx: `uvx ty check`

**Integration tips:**
- Ty automatically detects Python files in the current directory
- Integrates with LSP for real-time type checking in editors
- Supports inlay hints for variable types in VS Code, Neovim, and Zed
- Use `--python` to specify custom Python environment path
- Use `--config-file` to specify custom configuration file