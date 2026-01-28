#!/bin/bash

# MarketMind Pro - Automated Setup Script
# This script sets up the entire project on a fresh machine

echo "🚀 MarketMind Pro - Automated Setup"
echo "===================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if running on Windows (WSL)
if grep -qi microsoft /proc/version 2>/dev/null; then
    print_info "Detected WSL (Windows Subsystem for Linux)"
fi

# Step 1: Check Prerequisites
echo "📋 Step 1: Checking Prerequisites"
echo "=================================="

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3.11+ is required but not found"
    echo "Please install Python from: https://www.python.org/downloads/"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
else
    print_error "Node.js 18+ is required but not found"
    echo "Please install Node.js from: https://nodejs.org/"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION found"
else
    print_error "npm is required but not found"
    exit 1
fi

echo ""

# Step 2: Install Python Dependencies
echo "📦 Step 2: Installing Python Dependencies"
echo "=========================================="

print_info "Installing required Python packages..."
pip install fastapi uvicorn pydantic sqlalchemy redis matplotlib pillow reportlab > /dev/null 2>&1

if [ $? -eq 0 ]; then
    print_success "Python dependencies installed"
else
    print_error "Failed to install Python dependencies"
    exit 1
fi

echo ""

# Step 3: Install Frontend Dependencies
echo "🎨 Step 3: Installing Frontend Dependencies"
echo "==========================================="

if [ -d "frontend/react-app" ]; then
    cd frontend/react-app
    print_info "Installing npm packages (this may take a few minutes)..."
    npm install > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        print_success "Frontend dependencies installed"
    else
        print_error "Failed to install frontend dependencies"
        cd ../..
        exit 1
    fi
    
    cd ../..
else
    print_error "frontend/react-app directory not found"
    exit 1
fi

echo ""

# Step 4: Build Frontend
echo "🔨 Step 4: Building Frontend"
echo "============================="

cd frontend/react-app
print_info "Building React application..."
npm run build > /dev/null 2>&1

if [ $? -eq 0 ]; then
    print_success "Frontend built successfully"
else
    print_error "Failed to build frontend"
    cd ../..
    exit 1
fi

cd ../..

echo ""

# Step 5: Create necessary directories
echo "📁 Step 5: Creating Directories"
echo "================================"

mkdir -p logs
mkdir -p data
mkdir -p reports_storage

print_success "Directories created"

echo ""

# Step 6: Verify Installation
echo "🔍 Step 6: Verifying Installation"
echo "=================================="

# Check if main files exist
if [ -f "complete_production_system.py" ]; then
    print_success "Backend file found"
else
    print_error "Backend file missing"
    exit 1
fi

if [ -f "frontend/react-app/dist/index.html" ]; then
    print_success "Frontend build found"
else
    print_error "Frontend build missing"
    exit 1
fi

if [ -f "deploy_production.sh" ]; then
    chmod +x deploy_production.sh
    print_success "Deployment script ready"
else
    print_error "Deployment script missing"
    exit 1
fi

echo ""

# Step 7: Installation Complete
echo "🎉 Installation Complete!"
echo "========================="
echo ""
echo "Next steps:"
echo "1. Start the application:"
echo "   ${GREEN}./deploy_production.sh${NC}"
echo ""
echo "2. Open your browser:"
echo "   ${GREEN}http://localhost:3000${NC}"
echo ""
echo "3. Try the demo:"
echo "   - Enter ticker: ${GREEN}DEMO${NC}"
echo "   - Click 'Generate Report'"
echo "   - Wait ~30 seconds"
echo "   - View the report!"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Full documentation"
echo "   - DEVLOG.md - Development history"
echo ""
print_success "Setup completed successfully!"
