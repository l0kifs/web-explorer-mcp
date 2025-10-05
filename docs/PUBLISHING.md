# Publishing Guide

This guide explains how to publish `web-explorer-mcp` to PyPI so users can install it with `uvx`.

## Two Publishing Methods

Choose one of these methods:
- **Method A: GitHub Actions (Recommended)** - Automated, more secure, no local credentials needed
- **Method B: Manual Publishing** - Direct control, requires local setup with API tokens

---

## Method A: Publishing with GitHub Actions (Recommended)

This is the **recommended** approach - more secure and automated.

### Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org
2. **GitHub Repository**: Your code must be in a GitHub repository
3. **uv**: Ensure you have uv installed locally for testing builds

### One-Time Setup

#### Step 1: Create PyPI API Token

Generate an API token at https://pypi.org/manage/account/token/:
- **For first-time publishing**: Create a token with scope "Entire account" (you can't select a specific project that doesn't exist yet)
- Copy the token (it starts with `pypi-...`)

**Note:** After your first successful publish, you can create a project-specific token for better security.

#### Step 2: Add Token to GitHub Secrets

1. Go to your GitHub repository: https://github.com/l0kifs/web-explorer-mcp
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `PYPI_API_TOKEN`
5. Value: Paste your PyPI token
6. Click **Add secret**

#### Step 3: Create GitHub Actions Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v5
      with:
        enable-cache: true
    
    - name: Build package
      run: uv build
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

Commit and push this file:

```fish
mkdir -p .github/workflows
# Create the file with the content above
git add .github/workflows/publish.yml
git commit -m "ci: add PyPI publishing workflow"
git push origin main
```

#### Step 4: Verify Project Configuration

The `pyproject.toml` is already configured with:
- `build-system` using `uv_build`
- Package metadata (name, version, description)
- Entry point: `web-explorer-mcp`

### Publishing Process (GitHub Actions)

#### Step 1: Update Version

Edit the version in `pyproject.toml`:

```toml
[project]
name = "web-explorer-mcp"
version = "0.1.1"  # Increment this
```

Version format: `MAJOR.MINOR.PATCH`
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Step 2: Update Changelog

Create or update `CHANGELOG.md`:

```markdown
## [0.1.1] - 2025-10-06

### Added
- Docker Compose setup for SearxNG
- Installation scripts for bash and fish
- Configuration documentation

### Changed
- Improved README with quick start guide

### Fixed
- Bug fixes (if any)
```

#### Step 3: Test Build Locally (Optional but Recommended)

Before pushing a tag, test the build locally:

```fish
# Clean previous builds
rm -rf dist/

# Build the package
uv build
```

This creates:
- `dist/web_explorer_mcp-0.1.1-py3-none-any.whl` (wheel)
- `dist/web_explorer_mcp-0.1.1.tar.gz` (source distribution)

Test the local build:

```fish
# Install from local wheel
uvx --from ./dist/web_explorer_mcp-0.1.1-py3-none-any.whl web-explorer-mcp
```

#### Step 4: Commit and Create Tag

```fish
git add .
git commit -m "chore: bump version to 0.1.1"
git push origin main

# Create and push tag - this triggers the GitHub Action
git tag v0.1.1
git push origin v0.1.1
```

**That's it!** The GitHub Action will automatically:
1. Build the package
2. Publish to PyPI

#### Step 5: Monitor the Workflow

1. Go to https://github.com/l0kifs/web-explorer-mcp/actions
2. Watch the "Publish to PyPI" workflow run
3. Check for any errors

#### Step 6: Verify Installation

After the workflow succeeds (wait ~1-2 minutes):

```fish
# Test installation from PyPI
uvx web-explorer-mcp
```

#### Step 7: Update to Project-Specific Token (After First Publish)

For better security after your first successful publish:

1. Go to https://pypi.org/manage/project/web-explorer-mcp/settings/
2. Scroll to "API tokens" 
3. Create new token with scope "Project: web-explorer-mcp"
4. Update the `PYPI_API_TOKEN` secret in GitHub:
   - Go to GitHub repo → Settings → Secrets → Actions
   - Edit `PYPI_API_TOKEN` with the new project-specific token
5. Delete the old account-wide token at https://pypi.org/manage/account/token/

### Quick Reference (GitHub Actions Method)

```fish
# Update version in pyproject.toml
# Update CHANGELOG.md

# Test locally (optional)
rm -rf dist/ && uv build
uvx --from ./dist/web_explorer_mcp-X.Y.Z-py3-none-any.whl web-explorer-mcp

# Commit and tag
git add .
git commit -m "chore: bump version to X.Y.Z"
git push origin main
git tag vX.Y.Z
git push origin vX.Y.Z

# Done! GitHub Actions handles the rest
```

---

## Method B: Manual Publishing (Alternative)

Use this method if you prefer direct control or can't use GitHub Actions.

### Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org
2. **API Token**: Generate at https://pypi.org/manage/account/token/
   - For first publish: "Entire account" scope
   - After first publish: Create project-specific token
3. **uv**: Ensure you have uv installed

### One-Time Setup

Create or edit `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE
```

**Security Note:** Keep this token secure!

### Publishing Process (Manual)

#### Step 1-2: Update version and changelog (same as Method A)

#### Step 3: Build the Package

```fish
rm -rf dist/
uv build
```

#### Step 4: Publish to PyPI

```fish
uv publish
```

Or with explicit credentials:

```fish
uv publish --username __token__ --password pypi-YOUR_API_TOKEN_HERE
```

#### Step 5: Commit and Tag

```fish
git add .
git commit -m "chore: bump version to X.Y.Z"
git tag vX.Y.Z
git push origin main
git push origin vX.Y.Z
```

#### Step 6: Verify Installation

```fish
uvx web-explorer-mcp
```

### Quick Reference (Manual Method)

```fish
# Update version in pyproject.toml, update CHANGELOG.md
rm -rf dist/
uv build
uv publish
git add . && git commit -m "chore: bump version to X.Y.Z"
git tag vX.Y.Z
git push && git push --tags
```

---



## Trusted Publishing (More Secure)

Instead of using API tokens, configure trusted publishing:

1. Go to https://pypi.org/manage/project/web-explorer-mcp/settings/publishing/
2. Add GitHub as a trusted publisher:
   - Owner: `l0kifs`
   - Repository: `web-explorer-mcp`
   - Workflow: `publish.yml`
   - Environment: leave blank or create one

Then update the GitHub workflow to use trusted publishing (remove the password section).

## Troubleshooting

### "File already exists" error

You're trying to upload a version that already exists. Increment the version number.

### "Invalid credentials" error

Check your API token in `~/.pypirc` or the command line.

### Build errors

Ensure all dependencies are properly specified in `pyproject.toml`.

### Import errors after installation

Make sure the package structure is correct and `__init__.py` files exist.

## Quick Reference

```bash
# Full publish workflow
rm -rf dist/
uv build
uv publish --publish-url https://test.pypi.org/legacy/  # Test first
# If test works:
uv publish  # Publish to PyPI
git tag v0.1.1
git push origin v0.1.1
```

## Best Practices

1. **Always test on TestPyPI first**
2. **Use semantic versioning**
3. **Update CHANGELOG.md**
4. **Tag releases in Git**
5. **Keep credentials secure**
6. **Test installation before announcing**

## Resources

- [PyPI](https://pypi.org)
- [Test PyPI](https://test.pypi.org)
- [uv Publishing Docs](https://docs.astral.sh/uv/guides/publish/)
- [Semantic Versioning](https://semver.org)
