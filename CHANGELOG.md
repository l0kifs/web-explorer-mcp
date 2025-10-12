# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- None yet

### Changed
- None yet

### Fixed
- None yet

## [0.3.0] - 2025-10-12

### Added
- **Clean Architecture implementation** with clear layer separation:
  - `models/` layer for data entities (independent, no external dependencies)
  - `business/` layer for business logic and interface definitions
  - `integrations/` layer for external system integrations (Playwright, SearxNG)
  - `entrypoints/` layer for MCP server and dependency composition
- **New services architecture**:
  - `PlaywrightWebpageContentService` - modern content extraction using Playwright
  - `SearxngWebSearchService` - dedicated search service with proper error handling
  - `WebExplorerService` - main business service orchestrating search and content extraction
- **Comprehensive E2E test suite** for real-world scenarios:
  - GitHub Issues page content extraction tests
  - Stack Overflow page content extraction tests
  - General webpage content tool E2E tests
  - MCP server integration tests with real client
- **Unit tests** for all new services:
  - Business logic tests with mocked dependencies
  - Pagination utility tests
  - Service integration tests
- **Enhanced installation process**:
  - Automatic Playwright browsers installation
  - Improved error handling in installation scripts
  - Dependency validation during setup
- **Responsible use guidelines** in README:
  - Ethical web scraping practices
  - robots.txt compliance
  - Rate limiting recommendations
  - Terms of Service considerations
- **MCP client utility** for testing (`tests/mcp_client.py`)

### Changed
- **Refactored architecture** following Clean Architecture principles:
  - Clear separation of concerns across layers
  - Dependency inversion with protocol-based interfaces
  - Improved testability through dependency injection
- **Improved test structure**:
  - Separated unit tests from E2E tests
  - Added `slow` marker for tests requiring network access
  - Enhanced test configuration in pytest
- **Updated installation scripts** (`install.sh`, `install.fish`):
  - Better error messages and user feedback
  - Automatic browser installation for Playwright
  - Improved cross-platform compatibility
- **Enhanced configuration**:
  - Added browser timeout settings
  - Improved logging configuration
  - Better error handling in services
- **Updated documentation**:
  - Expanded CONFIGURATION.md with Playwright settings
  - Added architecture overview
  - Improved usage examples

### Removed
- **Legacy extractors** replaced by new service architecture:
  - Removed `web_search_extractor.py` (replaced by `SearxngWebSearchService`)
  - Removed `webpage_content_extractor.py` (replaced by `PlaywrightWebpageContentService`)
- **Deprecated test files** for old extractors

### Fixed
- Improved error handling in content extraction
- Better handling of dynamic content loading
- Enhanced reliability of web page parsing

## [0.2.0] - 2025-10-08

### Added
- **Pagination support** for webpage content extraction with `page` parameter
- **Enhanced content extraction** with semantic HTML parsing:
  - Separate `article_body` for primary content from `<article>`/`<main>` tags
  - Improved `main_text` extraction excluding article content to avoid duplication
  - Better HTML cleaning with extended tag removal (buttons, forms, SVG)
  - Meta description extraction from `<meta>` tags
- **Comprehensive test suite** with 65 tests achieving 92% code coverage
- **Python testing rules documentation** for consistent testing practices
- **Improved configuration**:
  - Added pytest-cov for coverage reporting
  - Enhanced pytest configuration with custom markers
  - Better coverage settings with branch coverage

### Changed
- **README.md**: Added comparison table with commercial alternatives, highlighting privacy benefits
- **Webpage content tool**: Now supports pagination and returns more structured data
- **Project structure**: Added complete test suite with fixtures and configuration
- **Dependencies**: Added pytest-cov for coverage reporting

### Fixed
- **HTML parsing**: Improved handling of malformed HTML and edge cases
- **Content extraction**: Better separation of article and complementary content

## [0.1.0] - 2025-10-06

### Added
- Initial release
- Web search tool using SearxNG
- Webpage content extraction tool
- MCP server implementation with FastMCP
- Configurable settings via environment variables
- Docker Compose setup for easy SearxNG deployment
- Installation scripts for bash and fish shells
- Comprehensive configuration documentation
- Uninstallation script for clean removal
- Publishing guide for maintainers
- Support for uvx-based installation

### Changed
- Updated README with quick start guide and architecture diagram
- Enhanced pyproject.toml with proper metadata for PyPI
- Improved .gitignore for Docker and build artifacts
