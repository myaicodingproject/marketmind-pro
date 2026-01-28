#!/bin/bash

# Quick Start Script for MarketMind Pro
echo "🚀 Quick Starting MarketMind Pro..."

# Start backend on port 8001
echo "📡 Starting backend server..."
python3 app_production_live.py --port 8001 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait a moment for backend to start
sleep 3

# Start frontend on port 8000
echo "🌐 Starting frontend server..."
cd frontend
PORT=8000 npm start &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

cd ..

echo ""
echo "✅ MarketMind Pro is starting up!"
echo "📊 Frontend: http://localhost:8000"
echo "🔧 Backend: http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop all servers"

# Save PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

# Wait for user interrupt
trap 'echo "Stopping servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f backend.pid frontend.pid; exit' INT

# Keep script running
wait