#!/bin/bash
# ============================================
# Superset Initialization Script (Bash)
# Personal Finance BI System - Phase 3
# ============================================

set -e

echo "============================================"
echo "  Personal Finance BI - Superset Setup"
echo "============================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if Docker is running
echo -e "${YELLOW}[1/5] Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Docker is not running. Please start Docker.${NC}"
    exit 1
fi
echo -e "  ${GREEN}Docker is running!${NC}"

# Navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
echo -e "  Working directory: $PROJECT_ROOT"

# Stop existing containers
echo ""
echo -e "${YELLOW}[2/5] Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true
echo -e "  ${GREEN}Done!${NC}"

# Build and start services
echo ""
echo -e "${YELLOW}[3/5] Building and starting services...${NC}"
docker-compose build superset superset-init

docker-compose up -d postgres
echo "  Waiting for PostgreSQL to be ready..."
sleep 10

# Start Superset
echo ""
echo -e "${YELLOW}[4/5] Starting Superset...${NC}"
docker-compose up -d superset
echo "  Waiting for Superset to initialize (this may take 2-3 minutes)..."

# Wait for Superset to be healthy
max_retries=30
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    health=$(docker inspect --format='{{.State.Health.Status}}' finance_superset 2>/dev/null || echo "starting")
    if [ "$health" = "healthy" ]; then
        echo -e "  ${GREEN}Superset is healthy!${NC}"
        break
    fi
    retry_count=$((retry_count + 1))
    echo "  Waiting... ($retry_count/$max_retries)"
    sleep 10
done

if [ $retry_count -ge $max_retries ]; then
    echo -e "${YELLOW}WARNING: Superset health check timed out. Continuing anyway...${NC}"
fi

# Run bootstrap
echo ""
echo -e "${YELLOW}[5/5] Running Superset bootstrap...${NC}"
docker-compose up superset-init

# Print summary
echo ""
echo "============================================"
echo -e "  ${GREEN}Setup Complete!${NC}"
echo "============================================"
echo ""
echo "  Services:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Backend API: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo -e "  - ${CYAN}Superset BI: http://localhost:8088${NC}"
echo "  - n8n Automation: http://localhost:5678"
echo "  - Mailhog: http://localhost:8025"
echo ""
echo "  Superset Credentials:"
echo "  - Username: admin"
echo "  - Password: admin"
echo ""
echo "  To start all services:"
echo -e "  ${YELLOW}docker-compose up -d${NC}"
echo ""
