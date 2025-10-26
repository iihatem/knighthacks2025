#!/bin/bash

# Restart Legal AI Agents - Clean and Start

echo "========================================="
echo "🔄 Restarting Legal AI Agents"
echo "========================================="
echo ""

# Step 1: Kill any processes on agent ports
echo "🔍 Checking for processes on ports 10001-10005..."
for port in 10001 10002 10003 10004 10005; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "   🔪 Killing process $pid on port $port"
        kill -9 $pid 2>/dev/null
        sleep 0.5
    fi
done

# Step 2: Also check for any Python processes running the agent manager
echo ""
echo "🔍 Checking for agent manager processes..."
pids=$(ps aux | grep "[s]tart_legal_agents\|[s]tart_a2a_agents" | awk '{print $2}')
if [ ! -z "$pids" ]; then
    echo "   🔪 Killing agent manager processes: $pids"
    echo "$pids" | xargs kill -9 2>/dev/null
    sleep 1
fi

echo ""
echo "✅ All ports cleared!"
echo ""

# Step 3: Start the agents
echo "🚀 Starting Legal AI Agents..."
echo ""

cd "$(dirname "$0")"
source venv/bin/activate
python3 start_legal_agents.py

