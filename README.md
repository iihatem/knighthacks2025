# Aura MM — AI-Powered Legal Case Management

An intelligent legal case management platform built for Morgan & Morgan, featuring multi-agent AI orchestration, document RAG search, and human-in-the-loop approval workflows. Built at Knight Hacks 2025.

---

## Overview

Aura MM assists lawyers and paralegals with end-to-end case management using a fleet of specialized AI agents. From processing evidence and drafting client emails to conducting legal research and scheduling depositions — every sensitive action is routed through an approval workflow before execution.

---

## Features

- **Case Management** — Create and manage cases with a `MM-YYYY-NNNNN` numbering scheme
- **Document Ingestion & RAG** — Ingest PDFs and images into a Snowflake vector store; semantic search across all case documents
- **Multi-Agent Orchestration** — An orchestrator routes user queries to specialized sub-agents
  - **Legal Researcher** — Gemini 2.5 Pro with Google Search grounding; finds precedents, citations, and rates case strength
  - **Client Communication Guru** — Drafts empathetic client emails; requires approval before sending
  - **Evidence Sorter** — Processes email attachments and categorizes evidence
  - **Records Wrangler** — Searches records via RAG and drafts record request emails
  - **Voice Scheduler** — Schedules depositions and mediations via Google ADK
- **Activity Approval Workflow** — All sensitive agent actions (emails, scheduling) are logged as pending activities requiring human approval before execution
- **Session Management** — Persistent, case-scoped conversation history across all agents
- **Salesforce Integration** — Case and task management synced with Salesforce CRM

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS v4 |
| Backend | Python, Flask |
| Database | Snowflake (vector embeddings via `EMBED_TEXT_768`) |
| AI / LLM | Google Gemini 2.5 Flash & Pro, Gemini Vision |
| File Storage | DigitalOcean Spaces (S3-compatible) |
| CRM | Salesforce |
| Email | SMTP (Gmail) |
| Voice | ElevenLabs |
| Scheduling | Google ADK (Agents Development Kit) + Google Calendar API |

---

## Project Structure

```
knighthacks2025/
├── backend/
│   ├── app.py                        # Main Flask application & all API routes
│   ├── requirements.txt
│   ├── services/
│   │   ├── activity_logger.py        # Logs agent actions to Snowflake
│   │   ├── session_manager.py        # Conversation session management
│   │   ├── email_sender.py           # SMTP email service
│   │   ├── evidence_processor.py     # Email attachment processing
│   │   └── salesforce_service.py     # Salesforce API integration
│   ├── agents/
│   │   └── orchistrator_agent/
│   │       ├── agent.py              # Routes queries to sub-agents
│   │       └── sub_agents/
│   │           ├── legal_researcher_agent/
│   │           ├── client_communication_agent/
│   │           ├── evidence_sorter_agent/
│   │           ├── records_wrangler_agent/
│   │           └── voice_scheduler_agent/
│   └── tools/
│       ├── communication_tools.py
│       └── salesforce_tools.py
└── frontend/
    ├── src/
    │   ├── app/                      # Next.js App Router pages
    │   │   ├── page.tsx              # Dashboard
    │   │   ├── cases/
    │   │   ├── case/[slug]/
    │   │   ├── clients/
    │   │   ├── client/[slug]/
    │   │   ├── calendar/
    │   │   ├── analytics/
    │   │   └── settings/
    │   ├── components/
    │   │   ├── Dashboard.tsx
    │   │   ├── GlobalChat.tsx        # Chat interface for agents
    │   │   ├── AddCaseModal.tsx
    │   │   └── ApprovalCard.tsx
    │   ├── lib/api.ts                # API client
    │   ├── hooks/
    │   │   ├── useCases.ts
    │   │   └── useRAG.ts
    │   └── types/case.ts
    └── package.json
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- A Snowflake account with vector search enabled
- Google Gemini API key
- DigitalOcean Spaces bucket (or any S3-compatible storage)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Fill in your credentials
python app.py                   # Starts on http://localhost:5001
```

### Frontend

```bash
cd frontend
npm install
npm run dev                     # Starts on http://localhost:3001
```

---

## Environment Variables

Create a `backend/.env` file with the following:

```env
# Google Gemini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

# Snowflake
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_DATABASE=
SNOWFLAKE_SCHEMA=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_ROLE=

# DigitalOcean Spaces (S3-compatible)
DO_SPACES_KEY=
DO_SPACES_SECRET=
DO_SPACES_BUCKET=
DO_SPACES_REGION=

# SMTP Email
FIRM_EMAIL=
FIRM_EMAIL_PASSWORD=
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
FIRM_NAME=

# Salesforce
SALESFORCE_CLIENT_ID=
SALESFORCE_CLIENT_SECRET=
SALESFORCE_INSTANCE_URL=
SALESFORCE_USERNAME=
SALESFORCE_PASSWORD=
SALESFORCE_SECURITY_TOKEN=

# ElevenLabs (voice)
ELEVENLABS_API_KEY=
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/create-case` | Create a new case |
| `GET` | `/api/list-cases` | List all cases |
| `GET` | `/api/view-case-data/<case_id>` | Get full case details and document chunks |
| `POST` | `/api/add-case-files` | Upload additional files to a case |
| `POST` | `/api/test-rag` | Semantic search across case documents |
| `POST` | `/api/agent/process` | Send a message to the orchestrator agent |
| `GET` | `/api/activities/<case_id>` | Get agent activities for a case |
| `POST` | `/api/activities/<activity_id>/approve` | Approve and execute a pending activity |
| `POST` | `/api/activities/<activity_id>/reject` | Reject a pending activity |
| `GET` | `/api/activities/pending` | Get all pending approvals |
| `GET` | `/api/sessions/<case_id>` | Get sessions for a case |
| `GET` | `/api/sessions/<session_id>/messages` | Get conversation history |
| `POST` | `/api/sessions/<session_id>/end` | End a session |
| `POST` | `/api/evidence/process-email` | Process an incoming email for evidence |

---

## Agent Architecture

```
User Message
      │
      ▼
[Orchestrator Agent]
      │  Analyzes intent + session history + case context
      │
      ├──► Legal Researcher       (Gemini 2.5 Pro + Google Search grounding)
      ├──► Client Communication   (email drafting → approval → SMTP send)
      ├──► Evidence Sorter        (email attachment categorization)
      ├──► Records Wrangler       (RAG search + record request emails)
      └──► Voice Scheduler        (Google ADK + Calendar API)
                │
                ▼
        [Activity Logger]         (if action requires human approval)
                │
                ▼
        Pending Approval Queue ◄── Lawyer approves/rejects in UI
                │
                ▼
           Execute Action
```

Sensitive actions (sending emails, scheduling calls, creating Salesforce tasks) are never executed automatically — they are logged as `pending` activities that must be approved by a lawyer before execution.

---

## Database Schema (Snowflake)

| Table | Purpose |
|---|---|
| `case_data` | Case metadata, document text chunks, and 768-dim vector embeddings |
| `agent_activities` | All agent actions with `pending`/`approved`/`rejected`/`completed` status |
| `agent_sessions` | Conversation sessions scoped to a case |
| `agent_messages` | Full message history within sessions |

Vector similarity search uses Snowflake's native `VECTOR_COSINE_SIMILARITY` and `EMBED_TEXT_768` functions.

---

## Frontend Pages

| Route | Page |
|---|---|
| `/` | Dashboard — recent cases, pending approvals, quick actions |
| `/cases` | All cases with filtering |
| `/case/[id]` | Case detail — documents, chat, activities |
| `/clients` | Client management |
| `/client/[id]` | Individual client profile |
| `/calendar` | Schedule depositions and meetings |
| `/analytics` | Case metrics and analytics |
| `/settings` | Application configuration |

---

## Built With

- [Google Gemini](https://ai.google.dev/) — Primary LLM and vision model
- [Snowflake](https://www.snowflake.com/) — Vector database and data warehouse
- [Next.js](https://nextjs.org/) — Frontend framework
- [Flask](https://flask.palletsprojects.com/) — Backend API
- [DigitalOcean Spaces](https://www.digitalocean.com/products/spaces) — File storage
- [Salesforce](https://www.salesforce.com/) — CRM integration
- [ElevenLabs](https://elevenlabs.io/) — Voice synthesis
- [Google ADK](https://google.github.io/adk-docs/) — Agent scheduling framework
