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
