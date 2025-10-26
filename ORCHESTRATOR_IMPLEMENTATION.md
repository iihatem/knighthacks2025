# 🎯 Orchestrator Implementation - All Logic in app.py

## ✅ What Was Changed

Per your request, I've moved **ALL** the orchestrator logic directly into `app.py`, eliminating any dependency on the `agents` directory.

---

## 📝 Key Changes

### **1. Added `orchestrator()` Function to app.py**

Location: `/backend/app.py` (lines 1060-1391)

This function now lives entirely in `app.py` and handles:

#### **Core Functionality:**

- ✅ Session management (create new or continue existing)
- ✅ Gemini-powered intent analysis
- ✅ Action type routing (research, email, appointments)
- ✅ Approval workflow (logs activities when needed)
- ✅ RAG integration for research queries
- ✅ Context-aware responses

#### **Action Types Implemented:**

| Action Type            | Description                   | Requires Approval | Implementation                          |
| ---------------------- | ----------------------------- | ----------------- | --------------------------------------- |
| `research_internal`    | Search case files using RAG   | ❌ No             | Uses `rag_search()` + Gemini synthesis  |
| `research_external`    | External legal research       | ❌ No             | Gemini provides research guidance       |
| `draft_email`          | Draft client emails           | ✅ Yes            | Gemini generates email + logs activity  |
| `schedule_appointment` | Schedule meetings/depositions | ✅ Yes            | Gemini extracts details + logs activity |
| `general_query`        | General questions             | ❌ No             | Gemini provides helpful response        |

---

## 🔄 How It Works

### **Step-by-Step Flow:**

```
1. User sends message → /api/agent/process endpoint
   ↓
2. Endpoint calls orchestrator(case_id, query, case_context, session_id)
   ↓
3. Orchestrator checks for existing session or creates new one
   ↓
4. Gemini analyzes the query to determine:
   - Is this a continuation or new topic?
   - What action type is needed?
   - Does it require approval?
   ↓
5. Routes to appropriate handler:
   ├─ research_internal → RAG search + Gemini synthesis
   ├─ research_external → Gemini research guidance
   ├─ draft_email → Gemini drafts email + logs activity
   ├─ schedule_appointment → Gemini extracts details + logs activity
   └─ general_query → Gemini provides response
   ↓
6. Stores messages in session for context
   ↓
7. Returns structured response to frontend
```

---

## 🎨 Example Interactions

### **1. Research Query (No Approval)**

```json
// User: "What injuries did the client suffer?"

// Orchestrator:
{
  "action_type": "research_internal",
  "requires_approval": false,
  "activity_logged": false,
  "result": "Based on the medical records, the client suffered fractured ribs, a concussion, and soft tissue damage...",
  "agent_response": {
    "action_type": "research_internal",
    "results_count": 5,
    "sources": ["medical_report.pdf", "police_report.pdf"],
    "answer": "..."
  }
}
```

### **2. Email Draft (Requires Approval)**

```json
// User: "Draft an email to John Smith about the settlement offer"

// Orchestrator:
{
  "action_type": "draft_email",
  "requires_approval": true,
  "activity_logged": true,
  "activity_id": "act-20251026-xyz",
  "result": "I've drafted an email for your approval. Please review it below.",
  "agent_response": {
    "to": "john.smith@email.com",
    "subject": "Important Update on Your Settlement Offer",
    "draft": "Dear John,\n\nI hope this email finds you well..."
  }
}
```

### **3. Appointment Scheduling (Requires Approval)**

```json
// User: "Schedule a meeting with the client for Thursday at 2pm"

// Orchestrator:
{
  "action_type": "schedule_appointment",
  "requires_approval": true,
  "activity_logged": true,
  "activity_id": "act-20251026-abc",
  "result": "I've prepared an appointment request for your approval...",
  "agent_response": {
    "appointment_type": "Client Meeting",
    "date": "2025-10-31",
    "time": "14:00",
    "duration": "60 minutes",
    "attendees": ["John Smith", "Lawyer"],
    "notes": "Discuss settlement offer details"
  }
}
```

---

## 🧩 Integration with Services

The orchestrator uses these service modules (which remain in `/backend/services/`):

### **1. Session Manager** (`services/session_manager.py`)

- `create_session()` - Creates new conversation session
- `get_active_session()` - Finds active session for a case
- `store_message()` - Stores user/agent messages
- `get_recent_messages()` - Retrieves last N messages for context

### **2. Activity Logger** (`services/activity_logger.py`)

- `log_agent_activity()` - Logs approval-needed actions
- Stores in Snowflake `agent_activities` table
- Links activities to sessions

### **3. RAG Search** (`app.py`)

- `rag_search()` - Vector similarity search in Snowflake
- Returns relevant case documents
- Used for `research_internal` queries

---

## 🎯 No Dependencies on `agents` Directory

### **Before:**

```python
# app.py was importing from agents directory
from agents.orchistrator_agent.agent import orchestrator
from agents.orchistrator_agent.sub_agents.client_communication_agent.agent import client_communication_guru
```

### **After:**

```python
# app.py now contains ALL orchestrator logic
def orchestrator(case_id, query, case_context, session_id):
    # All logic here - no imports from agents directory
    # Uses only:
    # - Gemini AI (genai.GenerativeModel)
    # - services/session_manager.py
    # - services/activity_logger.py
    # - rag_search() function in app.py
```

---

## 🚀 What's Working

✅ **Session Management**

- Automatically detects if query is continuation or new topic
- Maintains conversation context (last 5 messages)
- Creates new sessions when topic changes

✅ **Intent Analysis**

- Gemini analyzes each query to determine action type
- Classifies as research, email, appointment, or general
- Determines if approval is needed

✅ **Research Queries**

- Searches case files using RAG (vector similarity)
- Synthesizes results with Gemini
- No approval needed - executes immediately

✅ **Email Drafting**

- Gemini generates professional emails
- Extracts to/subject/body
- Logs activity for approval
- Frontend displays in approval card

✅ **Appointment Scheduling**

- Gemini extracts date/time/attendees
- Logs activity for approval
- Frontend displays in approval card

✅ **General Queries**

- Gemini provides helpful responses
- No approval needed
- Maintains conversation context

---

## 📊 Response Structure

The orchestrator returns a consistent structure:

```typescript
{
  status: "success",
  session_id: string,           // Current session ID
  session_mode: "new" | "continue",
  is_continuation: boolean,
  topic: string,                // Brief topic description
  action_type: string,          // research_internal, draft_email, etc.
  requires_approval: boolean,
  activity_logged: boolean,     // True if logged for approval
  activity_id?: string,         // Only if logged
  agent_type: string,           // Which "specialist" handled it
  result: string,               // Main response message
  agent_response: object,       // Structured data (email, appointment, etc.)
  reasoning: string             // Why this action was chosen
}
```

---

## 🔧 Configuration

### **Gemini Model:**

```python
model = genai.GenerativeModel('gemini-2.5-flash')
```

### **Session Context:**

- Retrieves last **5 messages** for context
- Sessions expire after **30 minutes** of inactivity (handled by session_manager)

### **RAG Search:**

- Top **5 results** for research queries
- Uses **300 characters** per result for context

---

## 🎓 Key Design Decisions

1. **All Logic in app.py**: No dependencies on `agents` directory
2. **Gemini for Everything**: Intent analysis, email drafting, appointment extraction, research synthesis
3. **Smart Session Management**: Automatically detects topic changes
4. **Selective Logging**: Only logs approval-needed actions (keeps UI clean)
5. **Graceful Fallbacks**: If JSON parsing fails, provides sensible defaults
6. **Context-Aware**: Uses RAG results and conversation history

---

## 🐛 Error Handling

The orchestrator includes robust error handling:

- **JSON Parsing**: Extracts JSON from markdown code blocks
- **Fallback Responses**: If Gemini fails, provides safe defaults
- **Session Recovery**: Creates new session if retrieval fails
- **RAG Failures**: Continues even if RAG search fails

---

## 📝 Testing

To test the orchestrator:

```bash
# 1. Start backend
cd /Users/mac/Desktop/knighthacks2025/backend
source venv/bin/activate
python3 app.py

# 2. Test research query
curl -X POST http://localhost:5001/api/agent/process \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "case-xyz",
    "query": "What injuries did the client suffer?"
  }'

# 3. Test email draft
curl -X POST http://localhost:5001/api/agent/process \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "case-xyz",
    "query": "Draft an email to the client about the settlement"
  }'

# 4. Test appointment
curl -X POST http://localhost:5001/api/agent/process \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "case-xyz",
    "query": "Schedule a meeting for Thursday at 2pm"
  }'
```

---

## ✅ Summary

**The orchestrator is now fully self-contained in `app.py`** with:

- ✅ No dependencies on `agents` directory
- ✅ All logic using Gemini AI directly
- ✅ Integration with services (session_manager, activity_logger)
- ✅ RAG search for research queries
- ✅ Approval workflow for emails and appointments
- ✅ Session management and context preservation
- ✅ Robust error handling and fallbacks

**Ready to use!** 🚀

---

_Implementation completed on October 26, 2025_
_All orchestrator logic now in `/backend/app.py`_
