#!/bin/bash

# MarketMind Pro Startup Script
# This script sets up and starts the MarketMind Pro backend

set -e

echo "🚀 Starting MarketMind Pro Backend Setup..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing!"
    echo "   Especially update DATABASE_URL, REDIS_URL, and SECRET_KEY"
    read -p "Press Enter to continue after editing .env file..."
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if Docker is available and start services
if command -v docker-compose &> /dev/null; then
    echo "🐳 Starting PostgreSQL and Redis with Docker Compose..."
    docker-compose up -d postgres redis
    
    # Wait for services to be ready
    echo "⏳ Waiting for database to be ready..."
    sleep 10
    
    # Run database migration
    echo "🗄️  Running database migration..."
    python migrate_db.py
else
    echo "⚠️  Docker Compose not found. Please ensure PostgreSQL and Redis are running manually."
    echo "   PostgreSQL: localhost:5432 (database: marketmind_pro)"
    echo "   Redis: localhost:6379"
    read -p "Press Enter when services are ready..."
fi

# Start the application
echo "🎯 Starting MarketMind Pro Backend..."
echo "   API Server: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   WebSocket: ws://localhost:8000/ws/{client_id}"
echo ""
echo "📊 Sample login credentials:"
echo "   Email: demo@marketmind.com"
echo "   Password: demo123456"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"

# Start the FastAPI server
uvicorn main_production:app --host 0.0.0.0 --port 8000 --reload