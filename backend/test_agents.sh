#!/bin/bash

# Quick test script for A2A agents

echo "========================================="
echo "Testing A2A Agent Servers"
echo "========================================="
echo ""

# Function to test an agent
test_agent() {
    local agent_name=$1
    local port=$2
    
    echo "Testing $agent_name (port $port)..."
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/.well-known/agent-card)
    
    if [ "$response" == "200" ]; then
        echo "✓ $agent_name is responding"
    else
        echo "✗ $agent_name is NOT responding (HTTP $response)"
    fi
}

# Test all agents
test_agent "Client Communication Agent" 10001
test_agent "Legal Researcher Agent" 10002
test_agent "Records Wrangler Agent" 10003
test_agent "Voice Scheduler Agent" 10004
test_agent "Evidence Sorter Agent" 10005

echo ""
echo "========================================="
echo "Testing Flask Backend"
echo "========================================="
echo ""

# Test Flask backend
echo "Testing Flask API..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health)

if [ "$response" == "200" ]; then
    echo "✓ Flask backend is responding"
else
    echo "✗ Flask backend is NOT responding (HTTP $response)"
fi

echo ""
echo "========================================="
echo "Test Complete"
echo "========================================="
echo ""

