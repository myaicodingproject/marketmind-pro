#!/bin/bash

# MarketMind Pro Production Deployment
echo "🚀 MarketMind Pro Production Deployment"
echo "========================================"

# Cleanup function
cleanup() {
    echo ""
    echo "🧹 Shutting down MarketMind Pro..."
    pkill -f "complete_production_system" 2>/dev/null || true
    pkill -f "react_server" 2>/dev/null || true
    echo "✅ Cleanup completed"
    exit 0
}

# Register cleanup function
trap cleanup EXIT INT TERM

# Create logs directory
mkdir -p logs

# Pre-deployment cleanup
echo "🧹 Pre-deployment cleanup..."
pkill -f "complete_production_system" 2>/dev/null || true
pkill -f "react_server" 2>/dev/null || true
sleep 2

# Check Python dependencies
echo "🔍 Checking dependencies..."
python3 -c "import fastapi, pydantic, sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Missing dependencies. Install with: pip install fastapi pydantic sqlalchemy"
fi


# Start backend
echo "🔧 Starting backend server..."
python3 complete_production_system.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
python3 frontend/server/react_server.py > logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# Wait for services to initialize
echo "⏳ Waiting for services to initialize..."
sleep 5

# Health checks
echo "🔍 Running health checks..."

# Backend health check
BACKEND_STATUS="❌"
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        BACKEND_STATUS="✅"
        break
    fi
    sleep 1
done

# Frontend health check  
FRONTEND_STATUS="❌"
for i in {1..10}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        FRONTEND_STATUS="✅"
        break
    fi
    sleep 1
done

# Display results
echo ""
echo "🎉 MarketMind Pro Production System Ready!"
echo "=========================================="
echo ""
echo "📊 System Information:"
echo "   Backend API:       http://localhost:8000"
echo "   Frontend UI:       http://localhost:3000"
echo "   Health Check:      http://localhost:8000/health"
echo "   API Docs:          http://localhost:8000/docs"
echo ""
echo "🔧 Service Status:"
echo "   Backend:           $BACKEND_STATUS"
echo "   Frontend:          $FRONTEND_STATUS"
echo ""
echo "📝 Log Files:"
echo "   Backend:           logs/backend.log"
echo "   Frontend:          logs/frontend.log"
echo ""
echo "🔧 Process IDs:"
echo "   Backend PID:       $BACKEND_PID"
echo "   Frontend PID:      $FRONTEND_PID"
echo ""
echo "🛑 To stop system: Press Ctrl+C (automatic cleanup)"
echo ""
echo "✅ PRODUCTION SYSTEM IS LIVE!"
echo "   👉 Visit http://localhost:3000 to generate reports"
echo "   👉 API available at http://localhost:8000"
echo ""

# Real-time monitoring
echo "📊 System Monitor (Press Ctrl+C to stop)"
echo "========================================"
START_TIME=$(date +%s)

# Monitor loop
while true; do
    TIMESTAMP=$(date +"%H:%M:%S")
    
    # Check if processes are running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "$TIMESTAMP ❌ Backend died (PID: $BACKEND_PID)"
        break
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "$TIMESTAMP ❌ Frontend died (PID: $FRONTEND_PID)"
        break
    fi
    
    # Show recent backend logs
    RECENT_LOGS=$(tail -n 1 logs/backend.log 2>/dev/null | tr -d '\0')
    
    if [[ -n "$RECENT_LOGS" ]]; then
        echo "$TIMESTAMP | $RECENT_LOGS"
    else
        # Show uptime
        UPTIME_SECONDS=$(($(date +%s) - START_TIME))
        UPTIME_MINS=$((UPTIME_SECONDS / 60))
        echo "$TIMESTAMP | System running | Uptime: ${UPTIME_MINS}m"
    fi
    
    sleep 3
done
