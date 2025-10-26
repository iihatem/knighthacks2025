# Python-Based Agent Manager - Upgrade Complete ✅

## 🎉 What Changed

I've replaced the shell script approach with a **Python-based server manager** modeled after your `start_a2a_agents.py` file. This is a **significant improvement** over bash scripts!

---

## 📁 New File Created

### `start_legal_agents.py`

A comprehensive Python script that:

- ✅ Manages all 5 legal AI agents
- ✅ Proper async/await with uvicorn
- ✅ Threading for background execution
- ✅ Graceful shutdown handling
- ✅ Better error messages
- ✅ Environment validation
- ✅ Cross-platform compatible

---

## 🆚 Comparison: Shell Scripts vs Python Manager

### Old Approach (Shell Scripts)

**`start_all_agents.sh`:**

```bash
#!/bin/bash
python3 -m agents.a2a_agents.client_communication.server &
python3 -m agents.a2a_agents.legal_researcher.server &
# ... etc
```

**Problems:**

- ❌ No error handling
- ❌ Hard to debug
- ❌ Process management issues
- ❌ No graceful shutdown
- ❌ Platform-specific (bash)
- ❌ PID file management messy

### New Approach (Python Manager)

**`start_legal_agents.py`:**

```python
class LegalAgentManager:
    async def start_all_servers(self):
        tasks = []
        for agent_name, port in agent_configs:
            task = asyncio.create_task(
                self.run_agent_server(...)
            )
            tasks.append(task)
        await asyncio.gather(*tasks)
```

**Benefits:**

- ✅ Proper error handling with try/except
- ✅ Clear error messages with logging
- ✅ Async/await for proper concurrency
- ✅ Graceful shutdown with signal handlers
- ✅ Cross-platform (Python)
- ✅ No PID files needed
- ✅ Easy to extend

---

## 🏗️ Architecture

### How It Works

```
start_legal_agents.py
    │
    ├─ LegalAgentManager
    │   ├─ setup_environment()      # Check API keys
    │   ├─ create_executors()       # Create agent executors
    │   ├─ create_agent_cards()     # Define agent capabilities
    │   └─ start_all_servers()      # Start all agents
    │
    └─ For each agent:
        ├─ Create A2A server
        ├─ Configure uvicorn
        ├─ Run in async task
        └─ Keep running until Ctrl+C
```

### Key Components

1. **Environment Setup**

   - Validates `GEMINI_API_KEY`
   - Loads `.env` file
   - Checks prerequisites

2. **Executor Creation**

   - Instantiates all 5 agent executors
   - Each executor wraps agent logic for A2A

3. **Agent Card Creation**

   - Defines capabilities for each agent
   - Specifies skills and examples
   - Sets ports and URLs

4. **Server Management**
   - Creates A2A Starlette applications
   - Configures uvicorn servers
   - Runs all servers concurrently
   - Handles graceful shutdown

---

## 🚀 How to Use

### Start All Agents

```bash
cd /Users/mac/Desktop/knighthacks2025/backend
source venv/bin/activate
python3 start_legal_agents.py
```

### What You'll See

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

### Stop All Agents

Just press `Ctrl+C` - it will gracefully shut down all servers.

---

## 🎯 Key Features

### 1. Proper Async/Await

```python
async def run_agent_server(self, agent_name, executor, agent_card, port):
    config = uvicorn.Config(app.build(), host='0.0.0.0', port=port)
    server = uvicorn.Server(config)
    await server.serve()
```

### 2. Threading for Background Execution

```python
def run_servers_in_background(self):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(self.start_all_servers())
```

### 3. Signal Handling

```python
def signal_handler(signum, frame):
    logger.info("🛑 Received shutdown signal...")
    manager.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

### 4. Error Handling

```python
try:
    self.executors = {
        'client_communication': ClientCommunicationExecutor(),
        # ... more agents
    }
except Exception as e:
    logger.error(f"❌ Failed to create executors: {e}")
    traceback.print_exc()
    return False
```

---

## 📊 Benefits Over Shell Scripts

| Feature               | Shell Scripts     | Python Manager               |
| --------------------- | ----------------- | ---------------------------- |
| **Error Handling**    | ❌ None           | ✅ Try/except with traceback |
| **Logging**           | ❌ Basic echo     | ✅ Structured logging        |
| **Async Support**     | ❌ Background &   | ✅ Proper async/await        |
| **Graceful Shutdown** | ❌ Kill processes | ✅ Signal handlers           |
| **Cross-Platform**    | ❌ Bash-specific  | ✅ Python everywhere         |
| **Debugging**         | ❌ Hard           | ✅ Easy with logs            |
| **Extensibility**     | ❌ Limited        | ✅ Object-oriented           |
| **Status Reporting**  | ❌ Basic          | ✅ Rich output               |

---

## 🔧 Customization

### Add a New Agent

1. **Create the agent files** (agent.py, executor.py)

2. **Import in `start_legal_agents.py`**:

```python
from agents.a2a_agents.new_agent.executor import NewAgentExecutor
from agents.a2a_agents.new_agent.agent import NewAgent
```

3. **Add to executors**:

```python
self.executors = {
    # ... existing agents
    'new_agent': NewAgentExecutor(),
}
```

4. **Add agent card**:

```python
self.agent_cards = {
    # ... existing cards
    'new_agent': AgentCard(
        name='New Agent',
        url='http://localhost:10006',
        description='Does something cool',
        # ... rest of config
    ),
}
```

5. **Add to server configs**:

```python
agent_configs = [
    # ... existing configs
    ('new_agent', 10006),
]
```

Done! The manager will automatically start your new agent.

---

## 🐛 Debugging

### Enable Debug Logging

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Check If Agents Are Running

```bash
# Test Agent Cards
curl http://localhost:10001/.well-known/agent-card
curl http://localhost:10002/.well-known/agent-card
# ... etc
```

### View Full Error Traces

The manager automatically prints full tracebacks when errors occur:

```python
except Exception as e:
    logger.error(f"❌ Failed: {e}")
    traceback.print_exc()  # Full stack trace
```

---

## 📚 Related Files

- **`start_legal_agents.py`** - Main Python manager (NEW)
- **`QUICK_START.md`** - Quick start guide
- **`DEPLOYMENT_GUIDE.md`** - Full deployment instructions
- **`start_all_agents.sh`** - Old shell script (deprecated but kept for reference)
- **`stop_all_agents.sh`** - Old stop script (deprecated)

---

## 🎓 What You Learned

By analyzing `start_a2a_agents.py` and adapting it, you now understand:

1. **Proper async server management** with uvicorn
2. **Threading patterns** for background execution
3. **Signal handling** for graceful shutdown
4. **Agent lifecycle management** in A2A
5. **Better error handling** with logging and tracebacks

---

## 🎉 Summary

✅ **Created**: `start_legal_agents.py` - Professional Python-based agent manager
✅ **Benefits**: Better error handling, logging, async support, graceful shutdown
✅ **Modeled After**: Your `start_a2a_agents.py` file
✅ **Status**: Ready to use!

**To start your agents:**

```bash
python3 start_legal_agents.py
```

**That's it!** Much better than shell scripts! 🚀
