#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[STOP]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

PID_DIR="./pids"

# Stop backend
if [ -f "$PID_DIR/backend.pid" ]; then
    PID=$(cat "$PID_DIR/backend.pid")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        log "Backend stopped (PID: $PID)"
    else
        log "Backend process not running"
    fi
    rm -f "$PID_DIR/backend.pid"
else
    log "No backend PID file found"
fi

# Stop frontend
if [ -f "$PID_DIR/frontend.pid" ]; then
    PID=$(cat "$PID_DIR/frontend.pid")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        log "Frontend stopped (PID: $PID)"
    else
        log "Frontend process not running"
    fi
    rm -f "$PID_DIR/frontend.pid"
else
    log "No frontend PID file found"
fi

# Stop Docker services
log "Stopping Docker services..."
docker-compose down

log "All services stopped"