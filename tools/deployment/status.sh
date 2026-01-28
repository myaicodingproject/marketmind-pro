#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[STATUS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

PID_DIR="./pids"
LOG_DIR="./logs"

echo "MarketMind Pro System Status"
echo "============================"

# Check processes
check_process() {
    local service=$1
    local pid_file="$PID_DIR/${service}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            log "$service running (PID: $pid)"
            return 0
        else
            error "$service not running (stale PID file)"
            return 1
        fi
    else
        warn "$service PID file not found"
        return 1
    fi
}

# Check services
check_process "backend"
check_process "frontend"

# Check Docker services
echo ""
log "Docker Services:"
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# Check endpoints
echo ""
log "Endpoint Status:"

# Backend health
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    log "Backend API: ✅ Healthy"
else
    error "Backend API: ❌ Not responding"
fi

# Frontend
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    log "Frontend: ✅ Accessible"
else
    error "Frontend: ❌ Not accessible"
fi

# Show recent logs
echo ""
log "Recent Logs (last 5 lines):"
if [ -f "$LOG_DIR/backend.log" ]; then
    echo "Backend:"
    tail -5 "$LOG_DIR/backend.log" | sed 's/^/  /'
fi

if [ -f "$LOG_DIR/frontend.log" ]; then
    echo "Frontend:"
    tail -5 "$LOG_DIR/frontend.log" | sed 's/^/  /'
fi