#!/bin/bash

# MarketMind Pro Data Pipeline Setup and Test Script
# Session C1: Data Pipeline Setup

echo "🚀 MarketMind Pro - Data Pipeline Setup (Session C1)"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run from backend directory."
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "🐍 Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Set environment variables for testing
export SEC_EDGAR_USER_AGENT="MarketMind Pro test@marketmind.com"

# Check if Alpha Vantage API key is set
if [ -z "$ALPHA_VANTAGE_API_KEY" ]; then
    echo "⚠️ Warning: ALPHA_VANTAGE_API_KEY not set. Alpha Vantage tests will be skipped."
    echo "   To get full functionality, sign up at https://www.alphavantage.co/support/#api-key"
else
    echo "✅ Alpha Vantage API key configured"
fi

echo ""
echo "🧪 Running Data Pipeline Tests..."
echo "================================="

# Run the test script
cd data
python3 test_pipeline.py
test_exit_code=$?

# Return to original directory
cd ..

echo ""
echo "📊 Test Results Summary:"
echo "======================="

if [ $test_exit_code -eq 0 ]; then
    echo "✅ All tests PASSED - Data pipeline is ready!"
elif [ $test_exit_code -eq 1 ]; then
    echo "⚠️ Tests PARTIALLY PASSED - Some components may need attention"
elif [ $test_exit_code -eq 2 ]; then
    echo "❌ Tests FAILED - Pipeline needs debugging"
else
    echo "💥 Test execution FAILED - Check error messages above"
fi

echo ""
echo "🎯 Next Steps:"
echo "============="
echo "1. Review test results above"
echo "2. If Alpha Vantage tests were skipped, consider getting an API key"
echo "3. Check the generated test data in ./test_marketmind.db (if created)"
echo "4. Run individual component tests if needed"

echo ""
echo "📁 Generated Files:"
echo "=================="
echo "- SQLite database: ./test_marketmind.db (cleaned up after test)"
echo "- ChromaDB: ./test_chroma_db/ (cleaned up after test)"
echo "- Logs: Check console output above"

echo ""
echo "🔧 Manual Testing Commands:"
echo "=========================="
echo "# Test SEC EDGAR only:"
echo "python3 -c \"import asyncio; from data.sec_edgar import SECEdgarClient; asyncio.run(SECEdgarClient().fetch_company_data('AAPL'))\""
echo ""
echo "# Test ChromaDB only:"
echo "python3 -c \"from data.chromadb_manager import ChromaDBManager; ChromaDBManager().get_stats()\""

exit $test_exit_code