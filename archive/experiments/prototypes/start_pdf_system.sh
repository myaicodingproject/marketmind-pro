#!/bin/bash

echo "🚀 Starting MarketMind Pro Enhanced PDF System"
echo "=============================================="

# Check if we're in the right directory
if [ ! -d "pdf_generator" ]; then
    echo "❌ Error: pdf_generator directory not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Create necessary directories
echo "📁 Creating output directories..."
mkdir -p test_output
mkdir -p test_downloads
mkdir -p generated_reports

# Start the PDF service in background
echo "🔧 Starting Enhanced PDF Service..."
cd pdf_generator
python3 api.py &
PDF_PID=$!
cd ..

# Wait for service to start
echo "⏳ Waiting for service to initialize..."
sleep 5

# Check if service is running
if kill -0 $PDF_PID 2>/dev/null; then
    echo "✅ PDF Service started successfully (PID: $PDF_PID)"
    
    # Run integration test
    echo "🧪 Running integration tests..."
    python3 test_integration.py
    
    # Keep service running for manual testing
    echo ""
    echo "🌐 PDF Service is running at: http://localhost:8002"
    echo "📊 Health check: http://localhost:8002/health"
    echo "📈 System status: http://localhost:8002/api/v1/system/status"
    echo ""
    echo "Press Ctrl+C to stop the service..."
    
    # Wait for user interrupt
    trap "echo '🛑 Stopping PDF service...'; kill $PDF_PID; exit 0" INT
    wait $PDF_PID
    
else
    echo "❌ Failed to start PDF service"
    exit 1
fi