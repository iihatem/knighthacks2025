# 📚 Aura MM Backend API Documentation

Base URL: `http://localhost:5001`

---

## 📋 Table of Contents

1. [**Case Management**](#1-case-management) - Create and manage legal cases
2. [**File Management**](#2-file-management) - Upload and manage case files
3. [**RAG & Search**](#3-rag--search) - Retrieve case information
4. [**AI Agents**](#4-ai-agents) - AI-powered case processing
5. [**Activity Logging & Approvals**](#5-activity-logging--approvals) - Track and approve agent actions
6. [**Debugging & Testing**](#6-debugging--testing) - System diagnostics
7. [**Health Check**](#7-health-check) - Server status

---

## 1. Case Management

### `POST /api/create-case`

**Purpose:** Create a new legal case with client metadata and optional files

**What it does:**

- Generates unique `case_id` (UUID) and `case_number` (MM-YYYY-NNNNN)
- Stores client information in Snowflake
- Processes uploaded files (PDF, images, text) if provided
- Builds RAG vector knowledge base from file content
- Supports creating cases without files (can add later)

**Request (FormData):**

```javascript
{
  case_name: "Smith vs ABC Insurance",      // Required
  client_name: "John Smith",                // Required
  client_phone: "(555) 123-4567",          // Optional
  client_email: "john@email.com",          // Optional
  files: [file1, file2, ...]               // Optional (can be empty)
}
```

**Success Response (201):**

```json
{
  "message": "Case created successfully!",
  "case_id": "case-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "case_number": "MM-2025-00001",
  "files_processed": 3
}
```

**Success Response - No Files (201):**

```json
{
  "message": "Case created successfully! You can add files later.",
  "case_id": "case-xyz...",
  "case_number": "MM-2025-00002"
}
```

**Error Response (400):**

```json
{
  "message": "Missing required fields: case_name and client_name are required"
}
```

**How it works:**

1. Validates required fields (`case_name`, `client_name`)
2. Generates `case_id` (UUID) and `case_number` (sequential)
3. **If no files:** Creates placeholder entry in Snowflake with metadata
4. **If files provided:**
   - Uploads each file to DigitalOcean Spaces
   - Processes PDFs: extracts text + converts image-only pages to descriptions
   - Processes images: uses Gemini Vision to describe content
   - Chunks text into manageable pieces
   - Generates vector embeddings using Snowflake's `EMBED_TEXT_768`
   - Stores text chunks + vectors in Snowflake with metadata
5. Returns case IDs

**Edge Cases:**

- ✅ Works with 0 files (creates metadata-only entry)
- ✅ Handles image-only PDF pages (Gemini Vision analysis)
- ✅ Auto-chunks large documents
- ✅ Duplicate case_name allowed (different case_id)
- ❌ Case number collision handled by incrementing

**Supported File Types:**

- PDFs (`.pdf`)
- Text files (`.txt`, `.eml`)
- Images (`.jpg`, `.jpeg`, `.png`)

---

### `GET /api/list-cases`

**Purpose:** List all cases with complete metadata for display

**What it does:**

- Retrieves all cases with case_number, case_name, client info
- Shows file count per case
- Sorted by case_number descending (newest first)
- Perfect for case list/dashboard display

**Request:**

```
GET /api/list-cases
```

**Success Response (200):**

```json
{
  "total_cases": 15,
  "cases": [
    {
      "case_id": "case-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "case_number": "MM-2025-00015",
      "case_name": "Smith vs ABC Insurance - Car Accident",
      "client_name": "John Smith",
      "client_phone": "(555) 123-4567",
      "client_email": "john.smith@email.com",
      "chunk_count": 42,
      "first_file": "https://bucket.../police_report.pdf"
    },
    {
      "case_id": "case-xyz...",
      "case_number": "MM-2025-00014",
      "case_name": "Johnson Case",
      "client_name": "Jane Johnson",
      "client_phone": null,
      "client_email": null,
      "chunk_count": 1,
      "first_file": "metadata-only"
    }
  ]
}
```

**How it works:**

1. Queries Snowflake grouping by `case_id`
2. Uses `MAX()` to get metadata from first chunk (metadata stored once per case)
3. Counts all chunks per case
4. Orders by `case_number` DESC (newest cases first)
5. Returns complete case list

**Edge Cases:**

- Returns empty array if no cases exist
- `client_phone`/`client_email` may be `null` if not provided
- Cases without files show `first_file: "metadata-only"`
- `chunk_count: 1` indicates no files uploaded yet

**Frontend Integration:**
Perfect for displaying in a table/list:

```tsx
cases.map(case => (
  <div key={case.case_id}>
    <h3>{case.case_number} - {case.case_name}</h3>
    <p>Client: {case.client_name}</p>
    <p>Files: {case.chunk_count > 1 ? `${case.chunk_count} documents` : 'No files'}</p>
  </div>
))
```

---

### `GET /api/view-case-data/<case_id>`

**Purpose:** View all stored data for a specific case

**What it does:**

- Retrieves all text chunks for a case
- Shows source files
- Truncates long text for display
- Useful for debugging/verification

**Request:**

```
GET /api/view-case-data/case-a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Success Response (200):**

```json
{
  "case_id": "case-...",
  "total_chunks": 42,
  "data": [
    {
      "case_id": "case-...",
      "source_url": "https://.../police_report.pdf",
      "text_chunk": "On January 5th, the plaintiff was involved in...",
      "text_length": 1247,
      "vector_size": 768
    }
  ]
}
```

**How it works:**

1. Queries Snowflake for all rows matching `case_id`
2. Orders by `source_url`
3. Truncates text to 200 chars for display
4. Returns full metadata

**Edge Cases:**

- Returns 404 if case_id doesn't exist
- Includes placeholder entries for cases without files

---

## 2. File Management

### `POST /api/add-case-files`

**Purpose:** Add files to an existing case (update RAG knowledge base)

**What it does:**

- Uploads new files to existing case
- Processes files same as create-case
- Updates RAG knowledge base with new content
- Does NOT duplicate metadata

**Request (FormData):**

```javascript
{
  case_id: "case-a1b2c3d4-...",  // Required
  files: [file1, file2, ...]     // Required (at least 1)
}
```

**Success Response (200):**

```json
{
  "message": "Successfully added 3 files to case case-abc...",
  "case_id": "case-abc...",
  "files_processed": 3
}
```

**Error Response (400):**

```json
{
  "message": "Missing required field: case_id"
}
```

**Error Response (400):**

```json
{
  "message": "No files provided"
}
```

**How it works:**

1. Validates `case_id` and files exist
2. For each file:
   - Uploads to DigitalOcean Spaces under `{case_id}/{filename}`
   - Processes based on file type (same as create-case)
   - Generates embeddings
   - Stores in Snowflake **without metadata** (metadata already exists)
3. Returns count of successfully processed files

**Edge Cases:**

- ✅ Can be called multiple times for same case
- ✅ Metadata not duplicated (stored once during create-case)
- ✅ RAG search automatically includes new content
- ❌ Cannot add files to non-existent case_id

**Snowflake Storage Pattern:**

```
case_id              | case_name | client_name | text_chunk
---------------------|-----------|-------------|------------------
case-abc-123         | Smith...  | John Smith  | Placeholder...    ← Original
case-abc-123         | NULL      | NULL        | Police report...  ← Added file 1
case-abc-123         | NULL      | NULL        | Medical records.. ← Added file 2
```

---

## 3. RAG & Search

### `POST /api/test-rag`

**Purpose:** Search case knowledge base using semantic similarity

**What it does:**

- Converts query to vector embedding
- Searches Snowflake for similar text chunks
- Returns top-k most relevant results
- Powers AI agents with case context

**Request (JSON):**

```json
{
  "case_id": "case-abc...",
  "query": "What injuries did the plaintiff suffer?",
  "top_k": 5 // Optional, default 5
}
```

**Success Response (200):**

```json
{
  "case_id": "case-abc...",
  "query": "What injuries did the plaintiff suffer?",
  "results_count": 5,
  "results": [
    {
      "text_chunk": "Medical examination revealed fractured ribs...",
      "source_url": "https://.../medical_report.pdf",
      "similarity_score": 0.923
    }
  ]
}
```

**Error Response (400):**

```json
{
  "error": "Missing case_id or query"
}
```

**How it works:**

1. Embeds the query text using Snowflake's `EMBED_TEXT_768`
2. Queries Snowflake using `VECTOR_COSINE_SIMILARITY`
3. Filters by `case_id`
4. Returns top-k results ordered by similarity (highest first)
5. Similarity score range: -1 (opposite) to 1 (identical)

**Edge Cases:**

- Returns empty array if no matching case_id
- Returns fewer than top_k if case has few chunks
- Searches ALL chunks for that case (original + added files)

**Similarity Score Interpretation:**

- `0.9 - 1.0`: Extremely relevant
- `0.7 - 0.9`: Highly relevant
- `0.5 - 0.7`: Moderately relevant
- `< 0.5`: Weakly relevant

---

## 4. AI Agents & Chat

### `POST /api/agent/process`

**Purpose:** Process chatbot queries with intelligent session management and selective approval logging

**What it does:**

- **Smart Session Management:** Automatically detects conversation continuity vs new topics
- **Selective Logging:** Only creates activity logs for approval-needed actions (emails, appointments)
- **Context Preservation:** Maintains last 5 messages for conversation coherence
- **AI Routing:** Uses Gemini to analyze intent and route to specialist agents
- **Human-in-the-Loop:** Flags approval-required actions for lawyer review

**Request (JSON):**

```json
{
  "case_id": "case-abc...",
  "query": "Draft an email to John Smith about his settlement offer",
  "session_id": "session-xyz..." // Optional: Provide to continue existing session
}
```

**Success Response - Research Query (No Approval Needed):**

```json
{
  "status": "success",
  "session_id": "session-abc123",
  "is_continuation": false,
  "topic": "Legal research on slip and fall cases",
  "action_type": "research_internal",
  "requires_approval": false,
  "result": "Based on our internal knowledge base, slip and fall cases typically...",
  "activity_logged": false
}
```

**Success Response - Email Draft (Approval Required):**

```json
{
  "status": "success",
  "session_id": "session-abc123",
  "is_continuation": true,
  "topic": "Client communication - settlement offer",
  "action_type": "draft_email",
  "requires_approval": true,
  "result": {
    "draft": "Dear John,\n\nI hope this email finds you well...",
    "to": "john@email.com",
    "subject": "Important Update on Your Settlement Offer"
  },
  "activity_logged": true,
  "activity_id": "act-20251026-xyz"
}
```

**Error Response (400):**

```json
{
  "status": "error",
  "message": "Missing case_id or query"
}
```

**How the Chatbot Works:**

**Step 1: Session Detection**

- If `session_id` provided → Use existing session
- Else → Check for active session in last 30 minutes
- Else → Create new session

**Step 2: Context Retrieval**

- Get last 5 messages from session for conversation context
- Format: `[{"role": "user", "content": "..."}, {"role": "agent", "content": "..."}]`

**Step 3: Gemini Analysis**

```json
{
  "is_continuation": true/false,
  "topic": "Brief description of conversation topic",
  "action_type": "research_internal | research_external | draft_email | schedule_appointment | general_query",
  "requires_approval": true/false
}
```

**Step 4: Session Management**

- **New Topic:** Create new session
- **Continuation:** Update existing session's `last_activity`
- Store user message in `session_messages`

**Step 5: Agent Routing & Processing**

| Action Type            | Agent                   | Logs Activity? | Requires Approval? |
| ---------------------- | ----------------------- | -------------- | ------------------ |
| `research_internal`    | RAG Search              | ❌ No          | ❌ No              |
| `research_external`    | Web Search              | ❌ No          | ❌ No              |
| `general_query`        | Gemini Analysis         | ❌ No          | ❌ No              |
| `draft_email`          | ClientCommunicationGuru | ✅ **Yes**     | ✅ **Yes**         |
| `schedule_appointment` | VoiceBot Scheduler      | ✅ **Yes**     | ✅ **Yes**         |

**Step 6: Activity Logging (Conditional)**

- **Only for approval-needed actions** (email, appointments)
- Creates entry in `agent_activities` table with `session_id`
- Links activity to conversation context
- Sets `activity_status: 'pending'`

**Step 7: Response Storage**

- Store agent response in `session_messages`
- Update session `message_count`
- Return structured response

**Conversation Flow Example:**

```
User: "Research slip and fall cases in New York"
→ Action: research_internal
→ Activity Logged: NO
→ Session: session-001 created

User: "What about comparative negligence?"
→ Action: research_internal (continuation)
→ Activity Logged: NO
→ Session: session-001 continued

User: "Draft an email to the client about this"
→ Action: draft_email
→ Activity Logged: YES ✅
→ Activity ID: act-20251026-001
→ Session: session-001 continued
→ Requires Approval: YES
```

**Current Agents:**

- **Orchestrator** - Main router with Gemini-powered topic detection
- **ClientCommunicationGuru** - Drafts empathetic client messages
- **VoiceBotScheduler** - (Placeholder) Appointment scheduling
- **LegalResearcher** - (Placeholder) Legal research

**Edge Cases:**

- ✅ Multiple research questions don't spam activity log
- ✅ Topic changes create new sessions automatically
- ✅ Session expires after 30 minutes of inactivity
- ✅ Failed Gemini analysis defaults to general_query
- ✅ All conversations stored for audit trail
- ❌ No actual email sending (returns draft only)

**Human-in-the-Loop:**

- Research queries: ✅ Execute immediately (no approval needed)
- Email drafts: ⏸️ Pending approval (logged in activities)
- Appointments: ⏸️ Pending approval (logged in activities)

**Benefits of Smart Session Management:**

1. **Clean Activity Dashboard** - Only shows actions needing approval
2. **Full Conversation History** - All messages stored in sessions
3. **Better Context** - Agent has access to last 5 messages
4. **Automatic Topic Detection** - No manual "new conversation" button
5. **Audit Trail** - Complete record of all interactions

---

## 5. Debugging & Testing

### `GET /api/debug/snowflake`

**Purpose:** Test Snowflake connection and configuration

**What it does:**

- Checks all environment variables
- Tests database connection
- Verifies schema/database settings
- Counts rows in case_data table

**Request:**

```
GET /api/debug/snowflake
```

**Success Response (200):**

```json
{
  "status": "success",
  "message": "✅ Snowflake connection working!",
  "env_variables": {
    "SNOWFLAKE_USER": "✅ Set",
    "SNOWFLAKE_PASSWORD": "✅ Set",
    "SNOWFLAKE_ACCOUNT": "✅ Set",
    "SNOWFLAKE_WAREHOUSE": "COMPUTE_WH",
    "SNOWFLAKE_DATABASE": "TENDER_FOR_LAWYERS_DB",
    "SNOWFLAKE_SCHEMA": "VECTOR_SCHEMA",
    "SNOWFLAKE_ROLE": "TENDER_APP_ROLE"
  },
  "connection_info": {
    "user": "ACCOUNTADMIN",
    "role": "TENDER_APP_ROLE",
    "database": "TENDER_FOR_LAWYERS_DB",
    "schema": "VECTOR_SCHEMA"
  },
  "case_data_rows": 156
}
```

**Error Response (500):**

```json
{
  "status": "error",
  "message": "Failed to connect to Snowflake",
  "env_variables": { ... }
}
```

**How it works:**

1. Checks all required environment variables
2. Attempts database connection
3. Executes test query (`SELECT CURRENT_USER()`)
4. Counts rows in `case_data` table
5. Returns diagnostic info

**Edge Cases:**

- Shows which env vars are missing
- Returns partial info even on connection failure
- Helps diagnose permission issues

---

### `GET /api/test-embedding`

**Purpose:** Test Snowflake embedding function and permissions

**What it does:**

- Tests `EMBED_TEXT_768` function
- Verifies CORTEX permissions
- Checks vector storage in database
- Diagnoses embedding issues

**Request:**

```
GET /api/test-embedding
```

**Success Response (200):**

```json
{
  "status": "success",
  "message": "✅ Embedding function is working!",
  "test_embedding": {
    "text": "The plaintiff suffered injuries in a car accident.",
    "vector_dimensions": 768,
    "first_5_values": [0.123, -0.456, 0.789, ...],
    "last_5_values": [...]
  },
  "database_status": {
    "total_rows": 156,
    "rows_with_vectors": 156,
    "rows_without_vectors": 0,
    "sample": {
      "case_id": "case-...",
      "source_url": "...",
      "text_length": 1247,
      "has_vector": true
    }
  },
  "diagnosis": {
    "embedding_works": true,
    "data_exists": true,
    "vectors_stored": true,
    "issue": null
  }
}
```

**Error Response - Permission Issue (500):**

```json
{
  "status": "error",
  "message": "❌ Error: Insufficient privileges...",
  "is_permission_error": true,
  "help": "This is likely a permissions issue...",
  "next_steps": [
    "Log into Snowflake web UI",
    "Run these commands:",
    "  USE ROLE ACCOUNTADMIN;",
    "  GRANT DATABASE ROLE SNOWFLAKE.CORTEX_EMBED_USER TO ROLE TENDER_APP_ROLE;"
  ]
}
```

**How it works:**

1. Generates test embedding for sample text
2. Checks if embedding function works
3. Queries database for vector statistics
4. Provides diagnostic recommendations
5. Detects permission errors automatically

**Edge Cases:**

- ✅ Detects missing CORTEX permissions
- ✅ Shows rows without vectors
- ✅ Provides fix instructions
- ❌ Won't work if Snowflake connection fails

**Common Issues Detected:**

- Missing `CORTEX_EMBED_USER` role
- Database has rows but no vectors
- Embedding function not available

---

## 7. Health Check

### `GET /`

**Purpose:** Verify server is running

**Request:**

```
GET /
```

**Success Response (200):**

```
Backend server is running!
```

**How it works:**

- Simple endpoint returning plain text
- Used for health checks and uptime monitoring

---

## 🔐 Environment Variables Required

```bash
# Snowflake
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=TENDER_FOR_LAWYERS_DB
SNOWFLAKE_SCHEMA=VECTOR_SCHEMA
SNOWFLAKE_ROLE=TENDER_APP_ROLE

# DigitalOcean Spaces (S3-compatible)
DO_SPACES_ACCESS_KEY=your_key
DO_SPACES_SECRET_KEY=your_secret
DO_SPACES_BUCKET=your_bucket
DO_SPACES_REGION=nyc3

# Gemini AI
GEMINI_API_KEY=your_api_key

# Salesforce (for AI agents)
SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_token
SALESFORCE_DOMAIN=login
```

---

## 🗂️ Database Schema

### Table: `case_data`

| Column             | Type               | Description                             |
| ------------------ | ------------------ | --------------------------------------- |
| `case_id`          | VARCHAR            | UUID identifier (e.g., case-abc-123...) |
| `case_number`      | VARCHAR            | Human-readable (e.g., MM-2025-00001)    |
| `case_name`        | VARCHAR(500)       | Case title                              |
| `client_name`      | VARCHAR(200)       | Client's full name                      |
| `client_phone`     | VARCHAR(20)        | Client's phone                          |
| `client_email`     | VARCHAR(200)       | Client's email                          |
| `source_url`       | VARCHAR            | File URL or "metadata-only"             |
| `text_chunk`       | VARCHAR            | Text content                            |
| `vector_embedding` | VECTOR(FLOAT, 768) | Snowflake vector                        |

**Indexes:**

- `idx_case_id` on `case_id`
- `idx_case_number` on `case_number`

---

## 🚀 Quick Start Examples

### Create a case with files

```bash
curl -X POST http://localhost:5001/api/create-case \
  -F "case_name=Smith vs ABC Insurance" \
  -F "client_name=John Smith" \
  -F "client_email=john@email.com" \
  -F "files=@police_report.pdf" \
  -F "files=@medical_records.pdf"
```

### Create a case without files

```bash
curl -X POST http://localhost:5001/api/create-case \
  -F "case_name=Johnson Case" \
  -F "client_name=Jane Johnson"
```

### Add files later

```bash
curl -X POST http://localhost:5001/api/add-case-files \
  -F "case_id=case-abc-123..." \
  -F "files=@witness_statement.pdf"
```

### Search case knowledge base

```bash
curl -X POST http://localhost:5001/api/test-rag \
  -H "Content-Type: application/json" \
  -d '{"case_id":"case-abc...","query":"What injuries occurred?"}'
```

### Use AI agent

```bash
curl -X POST http://localhost:5001/api/agent/process \
  -H "Content-Type: application/json" \
  -d '{"case_id":"case-abc...","query":"Draft email about settlement"}'
```

---

## 📊 API Summary Table

| Endpoint                        | Method | Category  | Purpose               | Auth Required |
| ------------------------------- | ------ | --------- | --------------------- | ------------- |
| `/`                             | GET    | Health    | Server status         | No            |
| `/api/create-case`              | POST   | Case Mgmt | Create new case       | No            |
| `/api/add-case-files`           | POST   | File Mgmt | Add files to case     | No            |
| `/api/list-cases`               | GET    | Case Mgmt | List all cases        | No            |
| `/api/view-case-data/<case_id>` | GET    | Case Mgmt | View case data        | No            |
| `/api/test-rag`                 | POST   | RAG       | Search knowledge base | No            |
| `/api/agent/process`            | POST   | AI        | AI task processing    | No            |
| `/api/debug/snowflake`          | GET    | Debug     | Test Snowflake        | No            |
| `/api/test-embedding`           | GET    | Debug     | Test embeddings       | No            |

**Note:** Authentication not yet implemented. All endpoints currently open.

---

## 5. Activity Logging & Approvals

> **Purpose:** Track approval-needed agent actions (emails, appointments), support human-in-the-loop workflow

**Key Concept:** Activities are ONLY created for actions requiring lawyer approval. Research queries and general questions are NOT logged here (see Session Management instead).

### `GET /api/activities/<case_id>`

**Purpose:** Get all approval-needed activities for a specific case

**What shows up here:**

- ✅ Email drafts
- ✅ Appointment scheduling requests
- ❌ Research queries (stored in sessions instead)
- ❌ General questions (stored in sessions instead)

**Query Parameters:**

- `status` (optional): Filter by `pending`, `approved`, `rejected`, `completed`, `failed`

**Example Request:**

```bash
curl http://localhost:5001/api/activities/case-12345
curl http://localhost:5001/api/activities/case-12345?status=pending
```

**Success Response (200):**

```json
{
  "case_id": "case-12345",
  "total_activities": 3,
  "activities": [
    {
      "activity_id": "act-20251026-a1b2c3d4",
      "case_id": "case-12345",
      "session_id": "session-xyz123",
      "agent_type": "ClientCommunicationGuru",
      "agent_action": "draft_email",
      "activity_status": "pending",
      "prompt": "Draft an email to John Smith about his settlement offer",
      "agent_response": "{\"draft\": \"Dear John...\"}",
      "action_data": {
        "draft": "Dear John...",
        "to": "john@email.com",
        "subject": "Your Settlement Offer"
      },
      "created_at": "2025-10-26T14:30:00",
      "requires_approval": true,
      "approved_by": null,
      "approved_at": null
    }
  ]
}
```

**Activity Status Flow:**

```
pending → approved → completed (after execution)
        ↘ rejected
```

---

### `POST /api/activities/<activity_id>/approve`

**Purpose:** Approve a pending agent action

**Request Body:**

```json
{
  "approved_by": "lawyer@firm.com"
}
```

**What happens:**

1. Updates `activity_status` to `'approved'`
2. Sets `approved_by` and `approved_at`
3. **Future:** Triggers execution (email sending, appointment booking)

**Success Response (200):**

```json
{
  "status": "success",
  "message": "Activity act-20251026-a1b2c3d4 approved",
  "activity_id": "act-20251026-a1b2c3d4"
}
```

**Example:**

```bash
curl -X POST http://localhost:5001/api/activities/act-20251026-a1b2c3d4/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by": "lawyer@firm.com"}'
```

---

### `POST /api/activities/<activity_id>/reject`

**Purpose:** Reject a pending agent action

**Request Body:**

```json
{
  "approved_by": "lawyer@firm.com",
  "reason": "Email tone too aggressive, needs revision"
}
```

**What happens:**

1. Updates `activity_status` to `'rejected'`
2. Sets `approved_by`, `approved_at`
3. Stores rejection reason in `execution_result`
4. Agent will NOT execute this action

**Success Response (200):**

```json
{
  "status": "success",
  "message": "Activity act-20251026-a1b2c3d4 rejected"
}
```

**Example:**

```bash
curl -X POST http://localhost:5001/api/activities/act-20251026-a1b2c3d4/reject \
  -H "Content-Type: application/json" \
  -d '{"approved_by": "lawyer@firm.com", "reason": "Not appropriate"}'
```

---

### `GET /api/activities/pending`

**Purpose:** Get all pending activities across ALL cases (global approval queue)

**Use Case:** Dashboard showing "All items awaiting your approval across all cases"

**Success Response (200):**

```json
{
  "total_pending": 12,
  "activities": [
    {
      "activity_id": "act-20251026-xyz",
      "case_id": "case-12345",
      "session_id": "session-abc",
      "agent_type": "VoiceBotScheduler",
      "agent_action": "schedule_appointment",
      "activity_status": "pending",
      "prompt": "Schedule appointment with client for Thursday at 2pm",
      "created_at": "2025-10-26T15:00:00",
      "requires_approval": true
    },
    {
      "activity_id": "act-20251026-def",
      "case_id": "case-67890",
      "session_id": "session-def",
      "agent_type": "ClientCommunicationGuru",
      "agent_action": "draft_email",
      "activity_status": "pending",
      "created_at": "2025-10-26T14:45:00"
    }
  ]
}
```

**Example:**

```bash
curl http://localhost:5001/api/activities/pending
```

**Dashboard Integration:**

```tsx
// React component example
const PendingApprovals = () => {
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    fetch("/api/activities/pending")
      .then((res) => res.json())
      .then((data) => setActivities(data.activities));
  }, []);

  return (
    <div>
      <h2>Pending Approvals ({activities.length})</h2>
      {activities.map((activity) => (
        <ActivityCard
          key={activity.activity_id}
          activity={activity}
          onApprove={() => approveActivity(activity.activity_id)}
          onReject={() => rejectActivity(activity.activity_id)}
        />
      ))}
    </div>
  );
};
```

---

## 6. Session Management & Conversation History

> **Purpose:** Track ALL chat conversations, maintain context, provide audit trail

**Key Concept:** Sessions store EVERY message (research, questions, emails, etc.). Activities only store approval-needed items.

### `GET /api/sessions/<case_id>`

**Purpose:** List all conversation sessions for a case

**Query Parameters:**

- `status` (optional): Filter by `'active'`, `'completed'`, `'needs_approval'`

**Example Request:**

```bash
curl http://localhost:5001/api/sessions/case-12345
curl http://localhost:5001/api/sessions/case-12345?status=active
```

**Success Response (200):**

```json
{
  "case_id": "case-12345",
  "total_sessions": 5,
  "sessions": [
    {
      "session_id": "session-abc123",
      "case_id": "case-12345",
      "agent_type": "Orchestrator",
      "topic": "Research slip and fall cases",
      "status": "active",
      "message_count": 8,
      "created_at": "2025-10-26T14:00:00",
      "last_activity": "2025-10-26T14:30:00",
      "completed_at": null
    },
    {
      "session_id": "session-xyz789",
      "case_id": "case-12345",
      "agent_type": "ClientCommunicationGuru",
      "topic": "Client communication - settlement offer",
      "status": "needs_approval",
      "message_count": 4,
      "created_at": "2025-10-26T13:00:00",
      "last_activity": "2025-10-26T13:15:00",
      "completed_at": null
    }
  ]
}
```

**Session Status:**

- `'active'` - Ongoing conversation (< 30 min since last message)
- `'completed'` - Conversation ended
- `'needs_approval'` - Contains pending approval items

---

### `GET /api/sessions/<session_id>/messages`

**Purpose:** View full conversation history for a session

**Use Case:**

- Audit trail - see what lawyer and AI discussed
- Context - understand how agent arrived at draft
- Debugging - review conversation flow

**Example Request:**

```bash
curl http://localhost:5001/api/sessions/session-abc123/messages
```

**Success Response (200):**

```json
{
  "session_id": "session-abc123",
  "case_id": "case-12345",
  "topic": "Research slip and fall cases",
  "message_count": 8,
  "messages": [
    {
      "message_id": "msg-001",
      "role": "user",
      "content": "Research slip and fall cases in New York",
      "timestamp": "2025-10-26T14:00:00"
    },
    {
      "message_id": "msg-002",
      "role": "agent",
      "content": "Based on our knowledge base, slip and fall cases in NY typically require...",
      "timestamp": "2025-10-26T14:00:05"
    },
    {
      "message_id": "msg-003",
      "role": "user",
      "content": "What about comparative negligence?",
      "timestamp": "2025-10-26T14:05:00"
    },
    {
      "message_id": "msg-004",
      "role": "agent",
      "content": "New York follows pure comparative negligence, meaning...",
      "timestamp": "2025-10-26T14:05:03"
    }
  ]
}
```

**Chat UI Integration:**

```tsx
// Display conversation in chat interface
const ChatHistory = ({ sessionId }) => {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    fetch(`/api/sessions/${sessionId}/messages`)
      .then((res) => res.json())
      .then((data) => setMessages(data.messages));
  }, [sessionId]);

  return (
    <div className="chat-container">
      {messages.map((msg) => (
        <div key={msg.message_id} className={`message ${msg.role}`}>
          <p>{msg.content}</p>
          <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
        </div>
      ))}
    </div>
  );
};
```

---

### `POST /api/sessions/<session_id>/end`

**Purpose:** Manually mark a session as completed

**Use Case:** User clicks "End Conversation" button in chat UI

**Success Response (200):**

```json
{
  "status": "success",
  "message": "Session session-abc123 ended",
  "session_id": "session-abc123"
}
```

**Example:**

```bash
curl -X POST http://localhost:5001/api/sessions/session-abc123/end
```

**What happens:**

1. Sets `status` to `'completed'`
2. Sets `completed_at` timestamp
3. Next message will create NEW session (not continue this one)

---

## 📊 Database Schema Updates

### Table: `agent_sessions` (NEW)

Tracks conversation sessions

| Column          | Type            | Description                       |
| --------------- | --------------- | --------------------------------- |
| `session_id`    | VARCHAR(100) PK | Unique session ID                 |
| `case_id`       | STRING          | Reference to case                 |
| `agent_type`    | VARCHAR(50)     | Orchestrator, ClientComm, etc.    |
| `topic`         | VARCHAR(500)    | AI-generated topic description    |
| `status`        | VARCHAR(20)     | active, completed, needs_approval |
| `created_at`    | TIMESTAMP_NTZ   | Session start time                |
| `last_activity` | TIMESTAMP_NTZ   | Last message time                 |
| `message_count` | INT             | Total messages in session         |
| `completed_at`  | TIMESTAMP_NTZ   | Session end time                  |

### Table: `session_messages` (NEW)

Stores all messages within sessions

| Column       | Type            | Description       |
| ------------ | --------------- | ----------------- |
| `message_id` | VARCHAR(100) PK | Unique message ID |
| `session_id` | VARCHAR(100)    | Session reference |
| `role`       | VARCHAR(20)     | 'user' or 'agent' |
| `content`    | TEXT            | Message content   |
| `timestamp`  | TIMESTAMP_NTZ   | Message time      |

### Table: `agent_activities` (UPDATED)

Added session linkage

| New Column   | Type         | Description                 |
| ------------ | ------------ | --------------------------- |
| `session_id` | VARCHAR(100) | Links to session (optional) |

**Relationship:**

```
Sessions (1) ──→ (Many) Messages
Sessions (1) ──→ (0-Many) Activities (only for approval-needed)
```

---

---

## ⚠️ Known Limitations & Future Work

1. **No Authentication** - All endpoints are public
2. **RAG Context Not Integrated** - Agent doesn't use RAG search yet
3. **No Email Sending** - Agents return drafts only (need execution after approval)
4. **No File Validation** - Accepts any file type
5. **No Rate Limiting** - Can be abused
6. **No Pagination** - `/api/list-cases` could be slow with many cases
7. **No Soft Delete** - Cases cannot be archived/deleted
8. **No Auto-Execution** - Approved activities don't auto-execute yet (future: email sending, appointment booking)
9. **No Real-Time Updates** - Dashboard needs polling (WebSockets not implemented)

---

**Last Updated:** October 26, 2025  
**API Version:** 3.0 (Added Session Management & Smart Chatbot)  
**Base URL:** http://localhost:5001

**Total Endpoints:** 16

- Case Management: 3 endpoints
- File Management: 1 endpoint
- RAG & Search: 1 endpoint
- AI Agents & Chat: 1 endpoint ⭐ (with smart session management)
- Activity Logging: 4 endpoints
- Session Management: 3 endpoints ✨ NEW
- Debugging: 2 endpoints
- Health Check: 1 endpoint
