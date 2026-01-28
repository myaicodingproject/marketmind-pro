#!/bin/bash

# Enhanced PDF Generation System Startup Script
# This script starts the necessary services and runs tests

set -e

echo "🚀 Starting Enhanced PDF Generation System"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is required but not installed"
    exit 1
fi

# Install dependencies for PDF generator
print_status "Installing PDF generator dependencies..."
cd pdf_generator
pip3 install -r requirements.txt
cd ..

# Install main app dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    print_status "Installing main application dependencies..."
    pip3 install -r requirements.txt
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p generated_reports
mkdir -p logs

# Function to start a service in background
start_service() {
    local service_name=$1
    local command=$2
    local port=$3
    local log_file=$4
    
    print_status "Starting $service_name on port $port..."
    
    # Check if port is already in use
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "$service_name appears to already be running on port $port"
        return 0
    fi
    
    # Start the service
    nohup $command > $log_file 2>&1 &
    local pid=$!
    echo $pid > ".${service_name,,}.pid"
    
    # Wait a moment and check if service started
    sleep 3
    if kill -0 $pid 2>/dev/null; then
        print_success "$service_name started successfully (PID: $pid)"
        return 0
    else
        print_error "Failed to start $service_name"
        return 1
    fi
}

# Function to check service health
check_service_health() {
    local service_name=$1
    local url=$2
    local max_attempts=10
    local attempt=1
    
    print_status "Checking $service_name health..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            print_success "$service_name is healthy"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - waiting for $service_name..."
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name health check failed"
    return 1
}

# Start PDF Generator Service
start_service "PDF-Generator" "python3 -m uvicorn pdf_generator.api:app --host 0.0.0.0 --port 8002" 8002 "logs/pdf_generator.log"

# Start Main Backend (if main.py exists)
if [ -f "app/main.py" ]; then
    start_service "Backend" "python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000" 8000 "logs/backend.log"
elif [ -f "main.py" ]; then
    start_service "Backend" "python3 -m uvicorn main:app --host 0.0.0.0 --port 8000" 8000 "logs/backend.log"
fi

# Wait for services to be ready
sleep 5

# Check service health
print_status "Performing health checks..."
check_service_health "PDF Generator" "http://localhost:8002/health"

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    check_service_health "Backend" "http://localhost:8000/api/system/status"
fi

# Run tests
print_status "Running enhanced PDF generation tests..."
if python3 test_enhanced_pdf_generation.py; then
    print_success "All tests passed! 🎉"
else
    print_warning "Some tests failed. Check the output above for details."
fi

# Display service information
echo ""
echo "=========================================="
echo "🌟 Enhanced PDF Generation System Status"
echo "=========================================="
echo "PDF Generator Service: http://localhost:8002"
echo "Backend Service: http://localhost:8000 (if running)"
echo ""
echo "📁 Generated reports will be saved in: ./generated_reports/"
echo "📋 Service logs are available in: ./logs/"
echo ""
echo "🔧 To stop services, run: ./stop_services.sh"
echo "📖 API Documentation: http://localhost:8002/docs"
echo ""

# Create stop script
cat > stop_services.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping Enhanced PDF Generation Services..."

# Function to stop service by PID file
stop_service() {
    local service_name=$1
    local pid_file=".${service_name,,}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            echo "Stopping $service_name (PID: $pid)..."
            kill $pid
            rm "$pid_file"
            echo "✅ $service_name stopped"
        else
            echo "⚠️  $service_name was not running"
            rm "$pid_file"
        fi
    else
        echo "⚠️  No PID file found for $service_name"
    fi
}

stop_service "PDF-Generator"
stop_service "Backend"

echo "🏁 All services stopped"
EOF

chmod +x stop_services.sh

print_success "Enhanced PDF Generation System is ready!"
print_status "Use 'curl -X POST http://localhost:8002/api/v1/reports/test/pdf -H \"Content-Type: application/json\" -d @sample_request.json' to test"