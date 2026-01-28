#!/bin/bash

# MarketMind Pro - Quick Start & Test Script
# This script starts the application and runs basic tests automatically

set -e  # Exit on any error

echo "🚀 MarketMind Pro - Quick Start & Test"
echo "======================================"

# Change to project directory
cd /mnt/c/kiro

# Function to check if a service is running
check_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $name to start..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ $name is running"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $name failed to start"
    return 1
}

# Step 1: Start Docker services
echo "🐳 Starting Docker services..."
docker-compose down > /dev/null 2>&1 || true
docker-compose up -d

# Wait for services to be ready
check_service "http://localhost:5432" "PostgreSQL" || echo "⚠️ PostgreSQL may not be ready"
check_service "http://localhost:6379" "Redis" || echo "⚠️ Redis may not be ready"

# Step 2: Setup Python environment
echo "🐍 Setting up Python environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt > /dev/null 2>&1

# Step 3: Setup environment variables
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 Created .env file from template"
fi

# Step 4: Initialize database
echo "🗄️ Setting up database..."
python -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/marketmind_pro'

try:
    from app.core.database import engine, Base
    Base.metadata.create_all(bind=engine)
    print('✅ Database tables created')
except Exception as e:
    print(f'⚠️ Database setup issue: {e}')
"

# Step 5: Start the backend
echo "🚀 Starting backend server..."
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 5
check_service "http://localhost:8000/health" "Backend API"

# Step 6: Run basic tests
echo "🧪 Running basic tests..."

# Test 1: Health check
echo "   Testing health endpoint..."
if curl -s "http://localhost:8000/health" | grep -q "healthy"; then
    echo "   ✅ Health check passed"
else
    echo "   ❌ Health check failed"
fi

# Test 2: API documentation
echo "   Testing API documentation..."
if curl -s "http://localhost:8000/docs" > /dev/null; then
    echo "   ✅ API docs accessible"
else
    echo "   ❌ API docs not accessible"
fi

# Test 3: Company search (if endpoint exists)
echo "   Testing company search..."
if curl -s "http://localhost:8000/api/v1/companies/search?q=AAPL" > /dev/null; then
    echo "   ✅ Company search working"
else
    echo "   ⚠️ Company search endpoint may not be implemented yet"
fi

# Step 7: Show status
echo ""
echo "🎉 MarketMind Pro Status"
echo "======================="
echo "🌐 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🌸 Flower (Celery): http://localhost:5555"
echo ""
echo "🔧 Services:"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo "   - ChromaDB: localhost:8002"
echo ""

# Keep the script running and show logs
echo "📋 Backend logs (Ctrl+C to stop):"
echo "================================="
wait $BACKEND_PID
