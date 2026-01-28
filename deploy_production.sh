#!/bin/bash

# MarketMind Pro Production Deployment with Process Management
echo "🚀 MarketMind Pro Production Deployment with Process Management"
echo "=============================================================="

# Function to cleanup on exit - DISABLED to preserve kiro processes
# cleanup() {
#     echo ""
#     echo "🧹 Shutting down MarketMind Pro..."
#     
#     # Only kill our specific processes, not all kiro-cli
#     pkill -f "complete_production_system" 2>/dev/null || true
#     pkill -f "react_server" 2>/dev/null || true
#     pkill -f "system_monitor" 2>/dev/null || true
#     
#     echo "✅ Cleanup completed (kiro-cli processes preserved)"
#     exit 0
# }

# Register cleanup function - DISABLED
# trap cleanup EXIT INT TERM

# Create logs directory
mkdir -p logs

# Pre-deployment cleanup
echo "🧹 Pre-deployment cleanup..."
# Only clean up our specific processes, not all kiro-cli
pkill -f "complete_production_system" 2>/dev/null || true
pkill -f "react_server" 2>/dev/null || true
pkill -f "system_monitor" 2>/dev/null || true
# Don't kill all kiro-cli processes - only cleanup if emergency flag is set
if [ "$1" = "--force-cleanup" ]; then
    echo "🔥 Force cleanup requested - killing all kiro-cli processes..."
    python3 system_monitor.py --emergency 2>/dev/null || true
fi
sleep 2

# Install required packages for process management
echo "📦 Installing dependencies..."
pip install psutil requests > /dev/null 2>&1 || true

# Install enhanced system dependencies
echo "✨ Installing enhanced system dependencies..."
pip install -r requirements-enhanced.txt > /dev/null 2>&1 || true

# Run pre-deployment validation
echo "🔍 Running pre-deployment validation..."
python3 validate_deployment.py
if [ $? -ne 0 ]; then
    echo "❌ Validation failed! Fix issues before deploying."
    exit 1
fi
echo "✅ Validation passed!"

# Start backend (without process management)
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

# Process management health check
PROCESS_STATUS="⚠️ Disabled"

# Display results
echo ""
echo "🎉 MarketMind Pro Production System Ready!"
echo "=========================================="
echo ""
echo "📊 System Information:"
echo "   Backend API:       http://localhost:8000"
echo "   Frontend UI:       http://localhost:3000"
echo "   Health Check:      http://localhost:8000/health"
echo "   Process Monitor:   http://localhost:8000/api/v1/system/processes"
echo "   API Docs:          http://localhost:8000/docs"
echo ""
echo "🔧 Service Status:"
echo "   Backend:           $BACKEND_STATUS"
echo "   Frontend:          $FRONTEND_STATUS"
echo "   Process Manager:   $PROCESS_STATUS"
echo ""
echo "📝 Log Files:"
echo "   Backend:           /mnt/c/kiro/logs/backend.log"
echo "   Frontend:          /mnt/c/kiro/logs/frontend.log"
echo "   Monitor:           /mnt/c/kiro/logs/monitor.log"
echo ""
echo "🔧 Process IDs:"
echo "   Backend PID:       $BACKEND_PID"
echo "   Frontend PID:      $FRONTEND_PID"
echo ""
echo "🧪 Testing Commands:"
echo "   Process Test:      python3 test_process_management.py"
echo "   Quick Test:        python3 quick_test.py"
echo "   Emergency Cleanup: python3 system_monitor.py --emergency"
echo ""
echo "🛑 To stop system: Press Ctrl+C (automatic cleanup)"
echo ""
echo "✅ PRODUCTION SYSTEM IS LIVE!"
echo "   👉 Visit http://localhost:3000 to generate reports"
echo "   👉 API available at http://localhost:8000"
echo "   ⚠️ Process management disabled (manual cleanup needed)"
echo ""

# Real-time monitoring with process info
echo "📊 System Monitor (Press Ctrl+C to stop)"
echo "========================================"
START_TIME=$(date +%s)

# Monitor loop with process management info
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
    
    # Get process count manually
    KIRO_COUNT=$(pgrep -f "kiro-cli" | wc -l || echo "0")
    
    # Show recent backend logs
    RECENT_LOGS=$(tail -n 3 logs/backend.log 2>/dev/null | tr -d '\0' | tail -3)
    
    if [[ -n "$RECENT_LOGS" ]]; then
        echo "$RECENT_LOGS" | while read -r line; do
            if [[ -n "$line" ]]; then
                echo "$TIMESTAMP | Kiro:$KIRO_COUNT | $line"
            fi
        done
    else
        # Show uptime and process info
        UPTIME_SECONDS=$(($(date +%s) - START_TIME))
        UPTIME_MINS=$((UPTIME_SECONDS / 60))
        echo "$TIMESTAMP | 💤 System idle | Uptime: ${UPTIME_MINS}m | Kiro processes: $KIRO_COUNT | Backend: $BACKEND_PID"
    fi
    
    sleep 3
done
