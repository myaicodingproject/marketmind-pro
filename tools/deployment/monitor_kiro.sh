#!/bin/bash
# Monitor Kiro CLI processes in real-time

echo "🔍 Monitoring Kiro CLI Activity..."
echo "=================================="
echo ""

while true; do
    TIMESTAMP=$(date +"%H:%M:%S")
    
    # Count active kiro-cli processes
    KIRO_COUNT=$(pgrep -f "kiro-cli" | wc -l)
    
    # Get CPU usage of kiro-cli processes
    CPU_USAGE=$(ps aux | grep "kiro-cli" | grep -v grep | awk '{sum+=$3} END {printf "%.1f", sum}')
    
    # Get memory usage
    MEM_USAGE=$(ps aux | grep "kiro-cli" | grep -v grep | awk '{sum+=$4} END {printf "%.1f", sum}')
    
    # Check if processes are active (CPU > 0)
    if (( $(echo "$CPU_USAGE > 0" | bc -l) )); then
        STATUS="🟢 ACTIVE"
    else
        STATUS="🔴 IDLE/STUCK"
    fi
    
    echo "$TIMESTAMP | Processes: $KIRO_COUNT | CPU: ${CPU_USAGE}% | Memory: ${MEM_USAGE}% | $STATUS"
    
    sleep 3
done
