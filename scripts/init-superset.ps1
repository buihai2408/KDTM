# ============================================
# Superset Initialization Script (PowerShell)
# Personal Finance BI System - Phase 3
# ============================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Personal Finance BI - Superset Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[1/5] Checking Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "  Docker is running!" -ForegroundColor Green

# Navigate to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot
Write-Host "  Working directory: $projectRoot" -ForegroundColor Gray

# Stop existing containers
Write-Host ""
Write-Host "[2/5] Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>&1 | Out-Null
Write-Host "  Done!" -ForegroundColor Green

# Build and start services
Write-Host ""
Write-Host "[3/5] Building and starting services..." -ForegroundColor Yellow
docker-compose build superset superset-init
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build containers." -ForegroundColor Red
    exit 1
}

docker-compose up -d postgres
Write-Host "  Waiting for PostgreSQL to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# Start Superset
Write-Host ""
Write-Host "[4/5] Starting Superset..." -ForegroundColor Yellow
docker-compose up -d superset
Write-Host "  Waiting for Superset to initialize (this may take 2-3 minutes)..." -ForegroundColor Gray

# Wait for Superset to be healthy
$maxRetries = 30
$retryCount = 0
while ($retryCount -lt $maxRetries) {
    $health = docker inspect --format='{{.State.Health.Status}}' finance_superset 2>&1
    if ($health -eq "healthy") {
        Write-Host "  Superset is healthy!" -ForegroundColor Green
        break
    }
    $retryCount++
    Write-Host "  Waiting... ($retryCount/$maxRetries)" -ForegroundColor Gray
    Start-Sleep -Seconds 10
}

if ($retryCount -ge $maxRetries) {
    Write-Host "WARNING: Superset health check timed out. Continuing anyway..." -ForegroundColor Yellow
}

# Run bootstrap
Write-Host ""
Write-Host "[5/5] Running Superset bootstrap..." -ForegroundColor Yellow
docker-compose up superset-init
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Bootstrap may have encountered issues. Check logs above." -ForegroundColor Yellow
}

# Print summary
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Services:" -ForegroundColor White
Write-Host "  - PostgreSQL: localhost:5432" -ForegroundColor Gray
Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor Gray
Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "  - Superset BI: http://localhost:8088" -ForegroundColor Cyan
Write-Host "  - n8n Automation: http://localhost:5678" -ForegroundColor Gray
Write-Host "  - Mailhog: http://localhost:8025" -ForegroundColor Gray
Write-Host ""
Write-Host "  Superset Credentials:" -ForegroundColor White
Write-Host "  - Username: admin" -ForegroundColor Gray
Write-Host "  - Password: admin" -ForegroundColor Gray
Write-Host ""
Write-Host "  To start all services:" -ForegroundColor White
Write-Host "  docker-compose up -d" -ForegroundColor Yellow
Write-Host ""
