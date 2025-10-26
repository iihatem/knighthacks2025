#!/bin/bash

echo "🧪 Testing A2A Agent Response Extraction"
echo "========================================"
echo ""

# Check if agents are running
echo "📡 Checking if agents are running..."
for PORT in 10001 10002 10003 10004 10005; do
    if lsof -ti:$PORT > /dev/null 2>&1; then
        echo "  ✅ Port $PORT is active"
    else
        echo "  ❌ Port $PORT is NOT running"
        echo "     Run: python3 start_legal_agents.py"
        exit 1
    fi
done

echo ""
echo "📋 Testing Client Communication Agent directly..."

# Test JSON-RPC call to agent
curl -X POST http://localhost:10001/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Draft an email to the client reminding them about tomorrow morning'\''s deposition"}],
        "messageId": "test-123",
        "metadata": {"case_id": "test-case"}
      }
    },
    "id": 1
  }' 2>/dev/null | python3 -m json.tool

echo ""
echo ""
echo "✅ If you see a proper JSON response above with 'task' and 'status', the agent is working!"
echo ""
echo "📝 Next steps:"
echo "   1. Restart Flask: python3 app.py"
echo "   2. Test in frontend: 'hey send a message to the client reminding him about tomorrow morning'\''s deposition'"
echo "   3. Check Flask logs for 'Extracted content length: XXX'"
echo ""

