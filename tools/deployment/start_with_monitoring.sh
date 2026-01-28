#!/bin/bash
"""
MarketMind Pro Production Startup with Process Management
Starts the system with proper process monitoring and cleanup
"""

set -e

echo "🚀 Starting MarketMind Pro with Process Management..."

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up processes..."
    python3 system_monitor.py --emergency
    pkill -f "complete_production_system.py" || true
    pkill -f "system_monitor.py" || true
    echo "✅ Cleanup completed"
}

# Register cleanup function
trap cleanup EXIT INT TERM

# Check if required files exist
if [ ! -f "process_manager.py" ]; then
    echo "❌ process_manager.py not found"
    exit 1
fi

if [ ! -f "complete_production_system.py" ]; then
    echo "❌ complete_production_system.py not found"
    exit 1
fi

if [ ! -f "system_monitor.py" ]; then
    echo "❌ system_monitor.py not found"
    exit 1
fi

# Install required packages
echo "📦 Installing required packages..."
pip install psutil requests fastapi uvicorn playwright yfinance || true

# Emergency cleanup before starting
echo "🧹 Pre-startup cleanup..."
python3 system_monitor.py --emergency

# Start the system monitor in background
echo "🔍 Starting system monitor..."
python3 system_monitor.py &
MONITOR_PID=$!

# Wait a moment for monitor to start
sleep 2

# Start the main production system
echo "🚀 Starting MarketMind Pro production system..."
python3 complete_production_system.py &
MAIN_PID=$!

echo "✅ MarketMind Pro started successfully!"
echo "📊 Main system PID: $MAIN_PID"
echo "🔍 Monitor PID: $MONITOR_PID"
echo ""
echo "🌐 Access the application at: http://localhost:8000"
echo "📊 Health check: http://localhost:8000/health"
echo "🔧 Process monitor: http://localhost:8000/api/v1/system/processes"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for main process
wait $MAIN_PID
