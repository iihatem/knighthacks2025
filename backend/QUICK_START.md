# Quick Start Guide - Legal AI A2A Agents

## 🚀 Starting the System (Python-Based)

We now use a **Python-based server manager** instead of shell scripts. This provides better:

- ✅ Error handling
- ✅ Lifecycle management
- ✅ Cross-platform compatibility
- ✅ Proper async/await support
- ✅ Graceful shutdown

---

## Step 1: Install Dependencies

```bash
cd /Users/mac/Desktop/knighthacks2025/backend
source venv/bin/activate
pip install -r requirements.txt
```

---

## Step 2: Start All A2A Agents

### Using Python Manager (Recommended)

```bash
cd /Users/mac/Desktop/knighthacks2025/backend
source venv/bin/activate
python3 start_legal_agents.py
```

This will start all 5 agents:

- 📧 Client Communication Agent (Port 10001)
- 📚 Legal Researcher Agent (Port 10002)
- 📁 Records Wrangler Agent (Port 10003)
- 📅 Voice Scheduler Agent (Port 10004)
- 🗂️ Evidence Sorter Agent (Port 10005)

**Output:**

```
============================================================
🚀 Starting Legal AI A2A Agent Manager...
============================================================
✅ Environment variables configured
GEMINI_API_KEY: ✅ Set
✅ Legal agent executors created successfully
✅ Agent cards created successfully
🚀 Starting client_communication on port 10001
🚀 Starting legal_researcher on port 10002
🚀 Starting records_wrangler on port 10003
🚀 Starting voice_scheduler on port 10004
🚀 Starting evidence_sorter on port 10005
============================================================
✅ All Legal AI A2A Agent Servers Started!
============================================================
   📧 Client Communication: http://localhost:10001
   📚 Legal Researcher:     http://localhost:10002
   📁 Records Wrangler:     http://localhost:10003
   📅 Voice Scheduler:      http://localhost:10004
   🗂️  Evidence Sorter:      http://localhost:10005
============================================================
🎯 Agents are now listening for frontend requests!
💡 Use Ctrl+C to stop all servers
============================================================
```

---

## Step 3: Start Flask Backend

In a **new terminal**:

```bash
cd /Users/mac/Desktop/knighthacks2025/backend
source venv/bin/activate
python3 app.py
```

**Output:**

```
 * Running on http://127.0.0.1:5000
```

---

## Step 4: Start Frontend

In a **new terminal**:

```bash
cd /Users/mac/Desktop/knighthacks2025/frontend
npm run dev
```

**Output:**

```
ready - started server on 0.0.0.0:3001
```

---

## 🧪 Testing

### Test Agent Health

```bash
# Test Client Communication Agent
curl http://localhost:10001/.well-known/agent-card

# Test Legal Researcher Agent
curl http://localhost:10002/.well-known/agent-card

# Test Records Wrangler Agent
curl http://localhost:10003/.well-known/agent-card

# Test Voice Scheduler Agent
curl http://localhost:10004/.well-known/agent-card

# Test Evidence Sorter Agent
curl http://localhost:10005/.well-known/agent-card
```

Each should return a JSON Agent Card.

### Test via Frontend

1. Open http://localhost:3001
2. Navigate to a case page
3. Use the chat to send queries:
   - "Draft an email to the client"
   - "Research similar cases"
   - "Schedule a meeting"
   - "What documents do we need?"

---

## 🛑 Stopping the System

### Stop Agents

Press `Ctrl+C` in the terminal running `start_legal_agents.py`

### Stop Flask

Press `Ctrl+C` in the terminal running `app.py`

### Stop Frontend

Press `Ctrl+C` in the terminal running `npm run dev`

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'a2a'"

**Solution:**

```bash
pip install a2a-sdk google-adk
```

### Issue: "Port already in use"

**Solution:**

```bash
# Find process using the port
lsof -i :10001

# Kill the process
kill -9 <PID>
```

### Issue: "GEMINI_API_KEY not set"

**Solution:**
Create a `.env` file in the backend directory:

```bash
GEMINI_API_KEY=your_api_key_here
```

---

## 📊 System Architecture

```
Frontend (Port 3001)
    ↓
Flask API (Port 5000)
    ↓
Host Orchestrator
    ↓
├── Client Communication Agent (Port 10001)
├── Legal Researcher Agent (Port 10002)
├── Records Wrangler Agent (Port 10003)
├── Voice Scheduler Agent (Port 10004)
└── Evidence Sorter Agent (Port 10005)
```

---

## 💡 Pro Tips

1. **Keep agents running** - The Python manager keeps all agents alive
2. **Check logs** - Errors are printed to console with timestamps
3. **Graceful shutdown** - Always use Ctrl+C to stop (not kill -9)
4. **Test individually** - Test each agent's Agent Card before using
5. **Monitor resources** - Watch CPU/memory usage with `top` or `htop`

---

## 🎯 What's Different from Shell Scripts?

### Old Approach (Shell Scripts)

- ❌ Hard to debug
- ❌ No proper error handling
- ❌ Process management issues
- ❌ Platform-specific

### New Approach (Python Manager)

- ✅ Better error messages
- ✅ Proper async/await
- ✅ Graceful shutdown
- ✅ Cross-platform
- ✅ Easier to extend

---

## 📚 Next Steps

1. ✅ Start agents with `python3 start_legal_agents.py`
2. ✅ Start Flask backend
3. ✅ Start frontend
4. ✅ Test via browser
5. ✅ Deploy to production when ready

**You're all set!** 🎉
