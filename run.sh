#!/bin/bash

# RectitudeAI Startup Script

set -e

echo "🚀 Starting RectitudeAI..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3.11 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}✓ Activating virtual environment${NC}"
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Copying from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env with your API keys before continuing${NC}"
    exit 1
fi

# Install dependencies if needed
if ! pip show fastapi > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Installing dependencies...${NC}"
    pip install -r requirements.txt
fi

# Create logs directory
mkdir -p logs

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Redis is not running. Please start Redis:${NC}"
    echo "   - Docker: docker run -d -p 6379:6379 redis:alpine"
    echo "   - Mac: brew services start redis"
    echo "   - Linux: sudo systemctl start redis"
    echo ""
    echo "Rate limiting will be disabled if Redis is not available."
fi

# Start the server
echo -e "${GREEN}✓ Starting FastAPI server...${NC}"
echo ""
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health/"
echo ""
PYTHONPATH=. uvicorn backend.gateway.main:app --reload --port 8000
