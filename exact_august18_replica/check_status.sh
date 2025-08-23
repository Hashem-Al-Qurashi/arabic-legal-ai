#!/bin/bash
# Quick status check script

echo "🕌 Quranic Embedding Status Check"
echo "=================================="

# Check if process is running
if pgrep -f "quranic_embedding_processor" > /dev/null; then
    echo "✅ Process: RUNNING"
else
    echo "❌ Process: STOPPED"
fi

# Check database progress
if [ -f "data/quranic_foundations.db" ]; then
    VERSES=$(sqlite3 data/quranic_foundations.db "SELECT COUNT(*) FROM quranic_verses;" 2>/dev/null || echo "0")
    COST=$(sqlite3 data/quranic_foundations.db "SELECT ROUND(SUM(cost), 4) FROM quranic_verses;" 2>/dev/null || echo "0")
    echo "📊 Progress: $VERSES/3870 verses"
    echo "💰 Cost: \$$COST"
    
    if [ "$VERSES" -eq 3870 ]; then
        echo "🎉 COMPLETED!"
    fi
else
    echo "📊 Progress: No database yet"
fi

# Check for recent errors
if [ -f "logs/quranic_embedding.log" ]; then
    ERROR_COUNT=$(tail -50 logs/quranic_embedding.log | grep -i "error\|failed" | wc -l)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo "⚠️  Recent errors: $ERROR_COUNT"
        echo "Last error:"
        tail -50 logs/quranic_embedding.log | grep -i "error\|failed" | tail -1
    else
        echo "✅ No recent errors"
    fi
fi

echo "=================================="
echo "Last log entry:"
tail -1 logs/quranic_embedding.log 2>/dev/null || echo "No log file"