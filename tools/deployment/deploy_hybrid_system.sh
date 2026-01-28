#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[DEPLOY]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
PID_DIR="./pids"
LOG_DIR="./logs"

# Create directories
mkdir -p "$PID_DIR" "$LOG_DIR"

# Cleanup function
cleanup() {
    log "Cleaning up processes..."
    if [ -f "$PID_DIR/backend.pid" ]; then
        kill $(cat "$PID_DIR/backend.pid") 2>/dev/null || true
        rm -f "$PID_DIR/backend.pid"
    fi
    if [ -f "$PID_DIR/frontend.pid" ]; then
        kill $(cat "$PID_DIR/frontend.pid") 2>/dev/null || true
        rm -f "$PID_DIR/frontend.pid"
    fi
}

# Setup trap for cleanup
trap cleanup EXIT

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    command -v python3 >/dev/null 2>&1 || { error "Python 3 required"; exit 1; }
    command -v node >/dev/null 2>&1 || { error "Node.js required"; exit 1; }
    command -v docker >/dev/null 2>&1 || { error "Docker required"; exit 1; }
    
    log "Prerequisites check passed"
}

# Setup environment
setup_environment() {
    log "Setting up environment..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        warn "Created .env from template - please configure your settings"
    fi
    
    # Start Docker services
    docker-compose up -d postgres redis
    sleep 5
    
    log "Environment setup complete"
}

# Install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    # Backend dependencies
    cd backend
    pip install -r requirements.txt >/dev/null 2>&1
    cd ..
    
    # Frontend dependencies
    cd frontend-react
    npm install >/dev/null 2>&1
    cd ..
    
    log "Dependencies installed"
}

# Start backend server in background
start_backend() {
    log "Starting backend server..."
    
    cd backend
    nohup uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT \
        > "../$LOG_DIR/backend.log" 2>&1 &
    echo $! > "../$PID_DIR/backend.pid"
    cd ..
    
    # Wait for backend to be ready
    for i in {1..30}; do
        if curl -s http://localhost:$BACKEND_PORT/health >/dev/null 2>&1; then
            log "Backend server started (PID: $(cat $PID_DIR/backend.pid))"
            return 0
        fi
        sleep 1
    done
    
    error "Backend failed to start"
    return 1
}

# Start frontend server in background
start_frontend() {
    log "Starting frontend server..."
    
    cd frontend-react
    nohup npm start > "../$LOG_DIR/frontend.log" 2>&1 &
    echo $! > "../$PID_DIR/frontend.pid"
    cd ..
    
    # Wait for frontend to be ready
    for i in {1..60}; do
        if curl -s http://localhost:$FRONTEND_PORT >/dev/null 2>&1; then
            log "Frontend server started (PID: $(cat $PID_DIR/frontend.pid))"
            return 0
        fi
        sleep 1
    done
    
    error "Frontend failed to start"
    return 1
}

# Run validation
run_validation() {
    log "Running system validation..."
    
    if python3 validate_hybrid_system.py; then
        log "System validation passed"
        return 0
    else
        error "System validation failed"
        return 1
    fi
}

# Main deployment flow
main() {
    log "Starting MarketMind Pro deployment..."
    
    check_prerequisites
    setup_environment
    install_dependencies
    start_backend
    start_frontend
    run_validation
    
    log "Deployment complete!"
    log "Backend: http://localhost:$BACKEND_PORT"
    log "Frontend: http://localhost:$FRONTEND_PORT"
    log "API Docs: http://localhost:$BACKEND_PORT/docs"
    
    log "Process IDs saved in $PID_DIR/"
    log "Logs available in $LOG_DIR/"
    log "Run './stop_servers.sh' to stop all services"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        cleanup
        log "All services stopped"
        ;;
    "status")
        if [ -f "$PID_DIR/backend.pid" ] && kill -0 $(cat "$PID_DIR/backend.pid") 2>/dev/null; then
            log "Backend running (PID: $(cat $PID_DIR/backend.pid))"
        else
            warn "Backend not running"
        fi
        if [ -f "$PID_DIR/frontend.pid" ] && kill -0 $(cat "$PID_DIR/frontend.pid") 2>/dev/null; then
            log "Frontend running (PID: $(cat $PID_DIR/frontend.pid))"
        else
            warn "Frontend not running"
        fi
        ;;
    *)
        echo "Usage: $0 [deploy|stop|status]"
        exit 1
        ;;
esac