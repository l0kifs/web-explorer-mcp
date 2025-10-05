#!/usr/bin/env bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Web Explorer MCP Installer${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not available.${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running.${NC}"
    echo "Please start Docker and try again."
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is installed and running"

# Generate secret key for SearxNG if not already set
SETTINGS_FILE="searxng-config/settings.yml"
if [ -f "$SETTINGS_FILE" ]; then
    if grep -q "CHANGE_THIS_SECRET_KEY_ON_FIRST_RUN" "$SETTINGS_FILE"; then
        echo "Generating secret key for SearxNG..."
        SECRET_KEY=$(openssl rand -hex 32)
        
        # Use different sed syntax based on OS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/CHANGE_THIS_SECRET_KEY_ON_FIRST_RUN/$SECRET_KEY/g" "$SETTINGS_FILE"
        else
            # Linux
            sed -i "s/CHANGE_THIS_SECRET_KEY_ON_FIRST_RUN/$SECRET_KEY/g" "$SETTINGS_FILE"
        fi
        echo -e "${GREEN}✓${NC} Secret key generated"
    else
        echo -e "${GREEN}✓${NC} Secret key already configured"
    fi
fi

# Start SearxNG with Docker Compose
echo ""
echo "Starting SearxNG with Docker Compose..."
docker compose up -d

# Wait for SearxNG to be ready
echo "Waiting for SearxNG to start..."
RETRIES=30
until curl -s http://localhost:9011 > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
    echo -n "."
    sleep 1
    RETRIES=$((RETRIES - 1))
done
echo ""

if [ $RETRIES -eq 0 ]; then
    echo -e "${YELLOW}Warning: SearxNG might not be fully ready yet.${NC}"
    echo "You can check the status with: docker compose logs searxng"
else
    echo -e "${GREEN}✓${NC} SearxNG is running at http://localhost:9011"
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Install and run the MCP server:"
echo -e "   ${YELLOW}uvx web-explorer-mcp${NC}"
echo ""
echo "2. Or run it with uv if you have the project locally:"
echo -e "   ${YELLOW}uv run web-explorer-mcp${NC}"
echo ""
echo "3. Configure your AI client (e.g., Claude Desktop):"
echo "   See docs/CONFIGURATION.md for examples"
echo ""
echo "To stop SearxNG:"
echo -e "   ${YELLOW}docker compose down${NC}"
echo ""
echo "To view SearxNG logs:"
echo -e "   ${YELLOW}docker compose logs -f searxng${NC}"
echo ""
