# MarketMind Pro - Local Development Setup (No Docker)

Quick setup guide for running MarketMind Pro locally on Windows/WSL2 without Docker containers.

## Prerequisites

- Windows 10/11 with WSL2 enabled
- Python 3.11+
- Node.js 18+
- Git

## 1. Install PostgreSQL (WSL2)

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo service postgresql start

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE marketmind_pro;"
sudo -u postgres psql -c "CREATE USER marketmind WITH PASSWORD 'dev123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE marketmind_pro TO marketmind;"

# Install pgvector extension
sudo apt install postgresql-14-pgvector
sudo -u postgres psql marketmind_pro -c "CREATE EXTENSION vector;"
```

## 2. Install Redis (WSL2)

```bash
# Install Redis
sudo apt install redis-server

# Start Redis service
sudo service redis-server start

# Test Redis connection
redis-cli ping  # Should return PONG
```

## 3. Environment Configuration

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql://marketmind:dev123@localhost:5432/marketmind_pro

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys (replace with your keys)
OPENAI_API_KEY=your_openai_key_here
FINANCIAL_DATA_API_KEY=your_financial_api_key_here

# Application
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
API_V1_STR=/api/v1

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## 4. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python -m alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --port 8000
```

## 5. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend-react

# Install dependencies
npm install

# Start development server
npm start
```

## 6. Verify Installation

- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Database: `psql -h localhost -U marketmind -d marketmind_pro`
- Redis: `redis-cli ping`

## 7. Start Services Script

Create `start-dev.sh`:

```bash
#!/bin/bash

# Start services
sudo service postgresql start
sudo service redis-server start

# Start backend (in background)
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000 &

# Start frontend
cd frontend-react && npm start
```

Make executable: `chmod +x start-dev.sh`

## Troubleshooting

**PostgreSQL connection issues:**
```bash
# Check if PostgreSQL is running
sudo service postgresql status

# Reset password if needed
sudo -u postgres psql -c "ALTER USER marketmind PASSWORD 'dev123';"
```

**Redis connection issues:**
```bash
# Check Redis status
sudo service redis-server status

# Restart Redis
sudo service redis-server restart
```

**Python dependencies:**
```bash
# If pip install fails, try:
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

**Node.js issues:**
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## Development Workflow

1. Start services: `./start-dev.sh`
2. Access application at http://localhost:3000
3. Use Kiro CLI for development: `@prime` → `@plan-feature` → `@execute`
4. API documentation at http://localhost:8000/docs

## Performance Notes

- PostgreSQL runs natively (faster than Docker)
- Redis runs natively (lower latency)
- Hot reload enabled for both frontend and backend
- No container overhead