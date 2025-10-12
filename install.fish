#!/usr/bin/env fish

# Colors for output
set RED '\033[0;31m'
set GREEN '\033[0;32m'
set YELLOW '\033[1;33m'
set NC '\033[0m' # No Color

echo -e "$GREEN================================$NC"
echo -e "$GREEN Web Explorer MCP Installer $NC"
echo -e "$GREEN================================$NC"
echo ""

# Check if Docker is installed
if not command -v docker > /dev/null 2>&1
    echo -e "$RED Error: Docker is not installed.$NC"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
end

# Check if Docker Compose is available
if not docker compose version > /dev/null 2>&1
    echo -e "$RED Error: Docker Compose is not available.$NC"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
end

# Check if Docker daemon is running
if not docker info > /dev/null 2>&1
    echo -e "$RED Error: Docker daemon is not running.$NC"
    echo "Please start Docker and try again."
    exit 1
end

echo -e "$GREEN✓$NC Docker is installed and running"

# Generate secret key for SearxNG if not already set
set SETTINGS_FILE "searxng-config/settings.yml"
if test -f $SETTINGS_FILE
    if grep -q "CHANGE_THIS_SECRET_KEY_ON_FIRST_RUN" $SETTINGS_FILE
        echo "Generating secret key for SearxNG..."
        set SECRET_KEY (openssl rand -hex 32)
        sed -i "s/CHANGE_THIS_SECRET_KEY_ON_FIRST_RUN/$SECRET_KEY/g" $SETTINGS_FILE
        echo -e "$GREEN✓$NC Secret key generated"
    else
        echo -e "$GREEN✓$NC Secret key already configured"
    end
end

# Start services with Docker Compose
echo ""
echo "Starting SearxNG and Playwright with Docker Compose..."
docker compose up -d

# Wait for SearxNG to be ready
echo "Waiting for SearxNG to start..."
set RETRIES 30
while not curl -s http://localhost:9011 > /dev/null 2>&1; and test $RETRIES -gt 0
    echo -n "."
    sleep 1
    set RETRIES (math $RETRIES - 1)
end
echo ""

if test $RETRIES -eq 0
    echo -e "$YELLOW Warning: SearxNG might not be fully ready yet.$NC"
    echo "You can check the status with: docker compose logs searxng"
else
    echo -e "$GREEN✓$NC SearxNG is running at http://localhost:9011"
end

# Wait for Playwright to be ready
echo "Waiting for Playwright server to start..."
set RETRIES 30
while not curl -s http://localhost:9012 > /dev/null 2>&1; and test $RETRIES -gt 0
    echo -n "."
    sleep 1
    set RETRIES (math $RETRIES - 1)
end
echo ""

if test $RETRIES -eq 0
    echo -e "$YELLOW Warning: Playwright server might not be fully ready yet.$NC"
    echo "You can check the status with: docker compose logs playwright"
else
    echo -e "$GREEN✓$NC Playwright is running at http://localhost:9012"
end

echo ""
echo -e "$GREEN================================$NC"
echo -e "$GREEN Installation Complete!$NC"
echo -e "$GREEN================================$NC"
echo ""
echo "Next steps:"
echo ""
echo "1. Install and run the MCP server:"
echo -e "   $YELLOW uvx web-explorer-mcp$NC"
echo ""
echo "2. Or run it with uv if you have the project locally:"
echo -e "   $YELLOW uv run web-explorer-mcp$NC"
echo ""
echo "3. Configure your AI client (e.g., Claude Desktop):"
echo "   See docs/CONFIGURATION.md for examples"
echo ""
echo "To stop services:"
echo -e "   $YELLOW docker compose down$NC"
echo ""
echo "To view logs:"
echo -e "   $YELLOW docker compose logs -f searxng$NC"
echo -e "   $YELLOW docker compose logs -f playwright$NC"
echo ""
