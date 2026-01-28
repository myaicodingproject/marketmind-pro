#!/bin/bash
# debug_tools.sh - Quick debugging commands for hybrid system

echo "🔍 HYBRID SYSTEM DEBUG TOOLS"
echo "============================"

# Function to show available debug commands
show_debug_commands() {
    echo ""
    echo "Available debug commands:"
    echo "  debug env          - Check environment setup"
    echo "  debug quick        - Quick OpenAI test"
    echo "  debug full         - Full system debug"
    echo "  debug monitor      - Real-time monitoring"
    echo "  debug content      - Debug specific content"
    echo "  debug logs         - Show recent logs"
    echo "  debug status       - System status check"
    echo "  debug cleanup      - Clean debug files"
    echo ""
}

# Environment debug
debug_env() {
    echo "🔍 Environment Debug"
    echo "==================="
    python3 debug_monitor.py --mode env
}

# Quick debug
debug_quick() {
    echo "⚡ Quick Debug Test"
    echo "=================="
    python3 debug_monitor.py --mode quick
}

# Full debug
debug_full() {
    echo "🔍 Full System Debug"
    echo "==================="
    python3 debug_hybrid_system.py
}

# Real-time monitoring
debug_monitor() {
    echo "📡 Starting Real-time Monitor"
    echo "============================"
    echo "Press Ctrl+C to stop monitoring"
    python3 debug_monitor.py --mode monitor
}

# Debug specific content
debug_content() {
    if [ -z "$2" ]; then
        echo "Usage: debug content 'your content here'"
        return 1
    fi
    
    echo "🔍 Content Debug"
    echo "==============="
    python3 debug_monitor.py --content "$2"
}

# Show logs
debug_logs() {
    echo "📋 Recent Debug Logs"
    echo "==================="
    
    if [ -f "hybrid_debug.log" ]; then
        echo "--- Hybrid Debug Log (last 20 lines) ---"
        tail -20 hybrid_debug.log
    fi
    
    if [ -f "realtime_debug.log" ]; then
        echo ""
        echo "--- Real-time Debug Log (last 20 lines) ---"
        tail -20 realtime_debug.log
    fi
    
    if [ -f "hybrid_server.log" ]; then
        echo ""
        echo "--- Server Log (last 10 lines) ---"
        tail -10 hybrid_server.log
    fi
}

# System status
debug_status() {
    echo "📊 System Status Check"
    echo "====================="
    
    # Check if server is running
    if [ -f ".hybrid_server.pid" ]; then
        PID=$(cat .hybrid_server.pid)
        if ps -p $PID > /dev/null; then
            echo "✅ Server running (PID: $PID)"
        else
            echo "❌ Server not running (stale PID file)"
        fi
    else
        echo "❌ Server PID file not found"
    fi
    
    # Check API health
    echo ""
    echo "🌐 API Health Check:"
    curl -s http://localhost:8000/health | head -3 || echo "❌ API not responding"
    
    # Check debug files
    echo ""
    echo "📁 Debug Files:"
    for file in hybrid_debug.log realtime_debug.log hybrid_debug_report.json; do
        if [ -f "$file" ]; then
            size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
            echo "  ✅ $file (${size} bytes)"
        else
            echo "  ❌ $file (not found)"
        fi
    done
}

# Cleanup debug files
debug_cleanup() {
    echo "🧹 Cleaning Debug Files"
    echo "======================"
    
    files_to_clean=(
        "hybrid_debug.log"
        "realtime_debug.log"
        "hybrid_debug_report.json"
        "*_Debug_Test.pdf"
        "*_OpenAI_Enhanced.pdf"
    )
    
    for pattern in "${files_to_clean[@]}"; do
        if ls $pattern 1> /dev/null 2>&1; then
            rm -f $pattern
            echo "  🗑️  Removed: $pattern"
        fi
    done
    
    echo "✅ Debug cleanup complete"
}

# Main command handler
case "$1" in
    "env")
        debug_env
        ;;
    "quick")
        debug_quick
        ;;
    "full")
        debug_full
        ;;
    "monitor")
        debug_monitor
        ;;
    "content")
        debug_content "$@"
        ;;
    "logs")
        debug_logs
        ;;
    "status")
        debug_status
        ;;
    "cleanup")
        debug_cleanup
        ;;
    *)
        show_debug_commands
        ;;
esac
