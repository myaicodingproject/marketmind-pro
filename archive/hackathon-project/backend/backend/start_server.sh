#!/bin/bash
# MarketMind Pro Backend Startup Script

echo "Starting MarketMind Pro Backend..."

# Activate virtual environment
source venv/bin/activate

# Start the FastAPI server
echo "Starting FastAPI server on http://localhost:8000"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload