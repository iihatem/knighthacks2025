#!/bin/bash

# Kill processes on agent ports

echo "🔍 Finding processes on ports 10001-10005..."

for port in 10001 10002 10003 10004 10005; do
    pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "🔪 Killing process $pid on port $port"
        kill -9 $pid
    else
        echo "✓ Port $port is free"
    fi
done

echo ""
echo "✅ All agent ports are now free!"
echo ""
echo "You can now run: python3 start_legal_agents.py"

