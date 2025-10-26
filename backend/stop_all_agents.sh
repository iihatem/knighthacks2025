#!/bin/bash

# Stop all A2A agent servers

cd "$(dirname "$0")"

echo "========================================="
echo "Stopping A2A Agent Servers"
echo "========================================="
echo ""

# Function to stop an agent
stop_agent() {
    local agent_name=$1
    local pid_file="logs/${agent_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "Stopping $agent_name (PID: $pid)..."
            kill $pid
            rm "$pid_file"
            echo "✓ $agent_name stopped"
        else
            echo "✗ $agent_name not running (stale PID file)"
            rm "$pid_file"
        fi
    else
        echo "✗ $agent_name PID file not found"
    fi
}

# Stop all agents
stop_agent "Client Communication Agent"
stop_agent "Legal Researcher Agent"
stop_agent "Records Wrangler Agent"
stop_agent "Voice Scheduler Agent"
stop_agent "Evidence Sorter Agent"

echo ""
echo "========================================="
echo "All agents stopped"
echo "========================================="
echo ""

