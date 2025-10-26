# Legal AI Agents - A2A Implementation

This directory contains all the AI agents for the legal case management system, implemented using the A2A (Agent-to-Agent) protocol.

## Directory Structure

```
agents/
├── shared/                          # Shared utilities
│   └── base_executor.py            # Base class for all agent executors
│
├── orchestrator/                    # Host orchestrator
│   ├── __init__.py
│   └── host_agent.py               # Main orchestrator with A2A client
│
├── a2a_agents/                      # Specialist A2A agents
│   ├── client_communication/       # Port 10001
│   │   ├── __init__.py
│   │   ├── agent.py                # Agent logic
│   │   ├── executor.py             # A2A executor wrapper
│   │   └── server.py               # A2A HTTP server
│   │
│   ├── legal_researcher/           # Port 10002
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── executor.py
│   │   └── server.py
│   │
│   ├── records_wrangler/           # Port 10003
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── executor.py
│   │   └── server.py
│   │
│   ├── voice_scheduler/            # Port 10004
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── executor.py
│   │   └── server.py
│   │
│   └── evidence_sorter/            # Port 10005
│       ├── __init__.py
│       ├── agent.py
│       ├── executor.py
│       └── server.py
│
└── orchistrator_agent/             # [DEPRECATED - kept for reference]
    └── sub_agents/                 # Old monolithic implementation
```

## Agent Descriptions

### Host Orchestrator

**Location**: `orchestrator/host_agent.py`
**Function**: Main coordinator that:

- Discovers all specialist agents via Agent Cards
- Analyzes user intent using Gemini
- Routes tasks to appropriate specialist agents
- Aggregates and returns results

### Specialist Agents

#### 1. Client Communication Agent (Port 10001)

**Skills**: Draft emails, draft messages
**Requires Approval**: Yes
**Use Cases**:

- Draft emails to clients about case updates
- Compose messages about depositions
- Write client communications

**Example Query**: "Draft an email to the client about their upcoming deposition"

#### 2. Legal Researcher Agent (Port 10002)

**Skills**: Legal research, precedent finding
**Requires Approval**: No
**Use Cases**:

- Find relevant case law
- Research legal precedents
- Identify supporting verdicts
- Suggest legal theories

**Example Query**: "Find precedents for personal injury cases involving medical malpractice"

#### 3. Records Wrangler Agent (Port 10003)

**Skills**: Records management, document retrieval
**Requires Approval**: No
**Use Cases**:

- Identify missing documents
- Request records from providers
- Track document status
- Organize case files

**Example Query**: "What medical records are we still missing for this case?"

#### 4. Voice Scheduler Agent (Port 10004)

**Skills**: Appointment scheduling
**Requires Approval**: Yes
**Use Cases**:

- Schedule depositions
- Arrange mediations
- Set up client meetings
- Coordinate with multiple parties

**Example Query**: "Schedule a deposition for next Tuesday at 2 PM"

#### 5. Evidence Sorter Agent (Port 10005)

**Skills**: Evidence organization, document classification
**Requires Approval**: No
**Use Cases**:

- Classify documents
- Organize evidence by type
- Extract key evidence
- Maintain chain of custody

**Example Query**: "Organize all the evidence from the client's latest email"

## How to Run

### Start All Agents

```bash
cd /Users/mac/Desktop/knighthacks2025/backend
./start_all_agents.sh
```

### Start Individual Agent

```bash
cd /Users/mac/Desktop/knighthacks2025/backend
source venv/bin/activate

# Client Communication Agent
python3 -m agents.a2a_agents.client_communication.server --port 10001

# Legal Researcher Agent
python3 -m agents.a2a_agents.legal_researcher.server --port 10002

# Records Wrangler Agent
python3 -m agents.a2a_agents.records_wrangler.server --port 10003

# Voice Scheduler Agent
python3 -m agents.a2a_agents.voice_scheduler.server --port 10004

# Evidence Sorter Agent
python3 -m agents.a2a_agents.evidence_sorter.server --port 10005
```

### Stop All Agents

```bash
./stop_all_agents.sh
```

## Testing Agents

### Test Agent Card

```bash
curl http://localhost:10001/.well-known/agent-card | jq
```

### Test Agent Functionality

```bash
curl -X POST http://localhost:10001/message/send \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Draft an email to the client"}],
        "messageId": "test-123",
        "metadata": {"case_id": "test-case-001"}
      }
    },
    "id": 1
  }'
```

## Adding a New Agent

To add a new specialist agent:

1. **Create directory structure**:

   ```bash
   mkdir -p agents/a2a_agents/new_agent
   ```

2. **Create agent.py** (agent logic):

   ```python
   class NewAgent:
       SYSTEM_INSTRUCTION = """Your agent's instructions..."""
       SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

       def __init__(self):
           # Initialize Gemini, etc.
           pass

       async def ainvoke(self, query: str, case_context: str, session_id: str):
           # Process the request
           return {
               'is_task_complete': True,
               'require_user_input': False,
               'content': 'Response text',
               'metadata': {}
           }
   ```

3. **Create executor.py** (A2A wrapper):

   ```python
   from agents.shared.base_executor import BaseAgentExecutor
   from agents.a2a_agents.new_agent.agent import NewAgent

   class NewAgentExecutor(BaseAgentExecutor):
       def __init__(self):
           super().__init__('NewAgent')
           self.agent = NewAgent()

       async def process_task(self, query, case_id, session_id):
           return await self.agent.ainvoke(query, f"Case: {case_id}", session_id)
   ```

4. **Create server.py** (HTTP server):

   ```python
   # See existing agents for template
   ```

5. **Update orchestrator** to include new agent URL

6. **Update startup script** to start new agent

## Architecture Patterns

### Agent Pattern

Each agent follows this pattern:

1. **Agent Class** (`agent.py`) - Core logic using Gemini
2. **Executor Class** (`executor.py`) - Wraps agent for A2A protocol
3. **Server** (`server.py`) - HTTP server exposing A2A endpoints

### Base Executor

All agents inherit from `BaseAgentExecutor` which:

- Implements A2A `AgentExecutor` interface
- Handles task lifecycle (submitted → working → completed)
- Manages event queuing
- Provides consistent error handling

### Orchestrator Pattern

The host orchestrator:

1. Discovers agents via Agent Cards
2. Analyzes user intent
3. Routes to appropriate agent
4. Returns aggregated results

## Debugging

### View Agent Logs

```bash
tail -f logs/Client\ Communication\ Agent.log
```

### Check Agent Status

```bash
ps aux | grep "agents.a2a_agents"
```

### Test Agent Discovery

```bash
# From Python
from agents.orchestrator.host_agent import HostOrchestrator
import asyncio

async def test():
    orch = await HostOrchestrator.create()
    print(orch.get_agents_description())

asyncio.run(test())
```

## Environment Variables

Required for all agents:

- `GEMINI_API_KEY` - Gemini API key for AI processing

Optional (for enhanced functionality):

- `SNOWFLAKE_*` - For RAG context retrieval
- `DO_SPACES_*` - For file storage

## Resources

- **A2A Protocol**: https://a2a-protocol.org
- **Deployment Guide**: `../DEPLOYMENT_GUIDE.md`
- **Implementation Guide**: `../IMPLEMENTATION_GUIDE.md`
- **Analysis**: `../../A2A_PROTOCOL_ANALYSIS.md`
