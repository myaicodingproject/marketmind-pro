#!/bin/bash

# DEMO Mode - Quick Test Script
echo "🧪 Testing DEMO Mode Implementation"
echo "===================================="
echo ""

# Test 1: Check demo data exists
if [ -f "data/demo_report_aapl.json" ]; then
    echo "✅ Demo data file exists"
else
    echo "❌ Demo data file missing!"
    exit 1
fi

# Test 2: Validate JSON
python3 -c "import json; json.load(open('data/demo_report_aapl.json'))" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Demo data is valid JSON"
else
    echo "❌ Demo data is invalid JSON!"
    exit 1
fi

# Test 3: Check backend functions
if grep -q "def load_demo_data()" complete_production_system.py; then
    echo "✅ Backend demo functions present"
else
    echo "❌ Backend demo functions missing!"
    exit 1
fi

# Test 4: Check frontend build
if [ -d "frontend/react-app/dist" ]; then
    echo "✅ Frontend built successfully"
else
    echo "❌ Frontend not built!"
    exit 1
fi

# Test 5: Check frontend demo indicators
if grep -q "DEMO MODE" frontend/react-app/src/components/ReportViewerPage.jsx; then
    echo "✅ Frontend demo indicators added"
else
    echo "❌ Frontend demo indicators missing!"
    exit 1
fi

echo ""
echo "🎉 All checks passed!"
echo ""
echo "📝 To test DEMO mode:"
echo "   1. Run: ./deploy_production.sh"
echo "   2. Open: http://localhost:3000"
echo "   3. Enter: DEMO"
echo "   4. Click: Generate Research Report"
echo "   5. Wait: ~10 seconds"
echo "   6. See: Apple Inc. demo report with 🎭 DEMO MODE badge"
echo ""
echo "✅ DEMO mode is ready!"
