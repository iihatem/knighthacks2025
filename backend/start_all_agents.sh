#!/bin/bash

# Start all A2A agent servers
# This script starts all specialist agents in the background

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

echo "========================================="
echo "Starting A2A Agent Servers"
echo "========================================="
echo ""

# Function to start an agent
start_agent() {
    local agent_name=$1
    local agent_path=$2
    local port=$3
    
    echo "Starting $agent_name on port $port..."
    python3 -m $agent_path --port $port > "logs/${agent_name}.log" 2>&1 &
    local pid=$!
    echo "$pid" > "logs/${agent_name}.pid"
    echo "✓ $agent_name started (PID: $pid)"
}

# Create logs directory if it doesn't exist
mkdir -p logs

# Start all agents
start_agent "Client Communication Agent" "agents.a2a_agents.client_communication.server" 10001
sleep 2

start_agent "Legal Researcher Agent" "agents.a2a_agents.legal_researcher.server" 10002
sleep 2

start_agent "Records Wrangler Agent" "agents.a2a_agents.records_wrangler.server" 10003
sleep 2

start_agent "Voice Scheduler Agent" "agents.a2a_agents.voice_scheduler.server" 10004
sleep 2

start_agent "Evidence Sorter Agent" "agents.a2a_agents.evidence_sorter.server" 10005
sleep 2

echo ""
echo "========================================="
echo "All A2A agents started successfully!"
echo "========================================="
echo ""
echo "Agent endpoints:"
echo "  - Client Communication: http://localhost:10001"
echo "  - Legal Researcher:     http://localhost:10002"
echo "  - Records Wrangler:     http://localhost:10003"
echo "  - Voice Scheduler:      http://localhost:10004"
echo "  - Evidence Sorter:      http://localhost:10005"
echo ""
echo "To stop all agents, run: ./stop_all_agents.sh"
echo "To view logs: tail -f logs/<agent_name>.log"
echo ""

