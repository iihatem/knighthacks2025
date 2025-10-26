# 🗄️ Snowflake Database Setup Guide

## ❌ Current Issue

You're getting this error:

```
Table 'AGENT_SESSIONS' does not exist or not authorized.
```

This means the session management tables either don't exist or your role doesn't have access to them.

---

## ✅ Solution: Run These SQL Commands in Snowflake

### **Step 1: Log into Snowflake Web UI**

1. Go to your Snowflake web interface
2. Log in with your credentials
3. Make sure you're using a role with sufficient privileges (ACCOUNTADMIN or a role that can create tables)

---

### **Step 2: Run This SQL Script**

Copy and paste the following SQL commands into a Snowflake worksheet and run them:

```sql
-- ============================================
-- Session Management Tables Setup
-- ============================================

-- Switch to ACCOUNTADMIN role (or a role with CREATE TABLE privileges)
USE ROLE ACCOUNTADMIN;

-- Use your database and schema
USE DATABASE TENDER_FOR_LAWYERS_DB;
USE SCHEMA VECTOR_SCHEMA;

-- 1. Create agent_sessions table
CREATE TABLE IF NOT EXISTS agent_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    case_id VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50),
    topic VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    last_activity TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    message_count INT DEFAULT 0,
    completed_at TIMESTAMP_NTZ
);

-- 2. Create session_messages table
CREATE TABLE IF NOT EXISTS session_messages (
    message_id VARCHAR(100) PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT,
    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- 3. Create agent_activities table (if not exists)
CREATE TABLE IF NOT EXISTS agent_activities (
    activity_id VARCHAR(100) PRIMARY KEY,
    case_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100),
    agent_type VARCHAR(50),
    agent_action VARCHAR(100),
    activity_status VARCHAR(20) DEFAULT 'pending',
    prompt TEXT,
    agent_response TEXT,
    action_data TEXT,
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(200),
    approved_at TIMESTAMP_NTZ,
    execution_result TEXT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- 4. Grant privileges to your app role
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE agent_sessions TO ROLE TENDER_APP_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE session_messages TO ROLE TENDER_APP_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE agent_activities TO ROLE TENDER_APP_ROLE;

-- 5. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sessions_case_id ON agent_sessions(case_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON agent_sessions(status);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON session_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_activities_case_id ON agent_activities(case_id);
CREATE INDEX IF NOT EXISTS idx_activities_session_id ON agent_activities(session_id);
CREATE INDEX IF NOT EXISTS idx_activities_status ON agent_activities(activity_status);

-- 6. Verify tables were created
SHOW TABLES LIKE '%session%';
SHOW TABLES LIKE '%activities%';

-- 7. Verify grants
SHOW GRANTS ON TABLE agent_sessions;
SHOW GRANTS ON TABLE session_messages;
SHOW GRANTS ON TABLE agent_activities;

SELECT 'Setup complete! ✅' AS status;
```

---

### **Step 3: Verify Setup**

After running the script, verify the tables exist:

```sql
-- Check if tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'VECTOR_SCHEMA'
AND table_name IN ('AGENT_SESSIONS', 'SESSION_MESSAGES', 'AGENT_ACTIVITIES');

-- Check row counts (should be 0 initially)
SELECT 'agent_sessions' AS table_name, COUNT(*) AS row_count FROM agent_sessions
UNION ALL
SELECT 'session_messages', COUNT(*) FROM session_messages
UNION ALL
SELECT 'agent_activities', COUNT(*) FROM agent_activities;
```

---

## 📊 What These Tables Do

### **1. `agent_sessions`**

Tracks conversation sessions between users and the AI agent.

**Example row:**

```
session_id: sess-20251026-abc123
case_id: case-xyz
agent_type: Orchestrator
topic: Email drafting for client
status: active
created_at: 2025-10-26 10:30:00
last_activity: 2025-10-26 10:35:00
message_count: 5
```

### **2. `session_messages`**

Stores all messages within each session (full conversation history).

**Example rows:**

```
message_id: msg-001
session_id: sess-20251026-abc123
role: user
content: "Draft an email to the client"
timestamp: 2025-10-26 10:30:00

message_id: msg-002
session_id: sess-20251026-abc123
role: agent
content: "I've drafted an email for your approval..."
timestamp: 2025-10-26 10:30:15
```

### **3. `agent_activities`**

Logs actions that require approval (emails, appointments).

**Example row:**

```
activity_id: act-20251026-xyz
case_id: case-xyz
session_id: sess-20251026-abc123
agent_type: ClientCommunicationGuru
agent_action: draft_email
activity_status: pending
prompt: "Draft an email to the client"
agent_response: {"to": "client@email.com", "subject": "...", "draft": "..."}
requires_approval: true
created_at: 2025-10-26 10:30:15
```

---

## 🔍 Troubleshooting

### **Issue: "Table already exists but no privileges"**

**Solution:** Run the GRANT commands:

```sql
USE ROLE ACCOUNTADMIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE agent_sessions TO ROLE TENDER_APP_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE session_messages TO ROLE TENDER_APP_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE agent_activities TO ROLE TENDER_APP_ROLE;
```

### **Issue: "Role ACCOUNTADMIN not granted"**

**Solution:** Either:

1. Ask your Snowflake admin to grant you ACCOUNTADMIN
2. OR ask them to run the setup script for you
3. OR use a different role that has CREATE TABLE privileges

### **Issue: "Database or schema not found"**

**Solution:** Update the database/schema names in the script:

```sql
USE DATABASE YOUR_DATABASE_NAME;
USE SCHEMA YOUR_SCHEMA_NAME;
```

---

## ✅ After Setup

Once the tables are created and privileges granted:

1. **Restart your backend** (if it's running):

   ```bash
   cd /Users/mac/Desktop/knighthacks2025/backend
   source venv/bin/activate
   python3 app.py
   ```

2. **Test the chatbot** in your frontend:
   - Navigate to any case page
   - Try: "Draft a message to our client Daniel reminding him about tomorrow's deposition"
   - It should work now! ✅

---

## 📝 Quick Copy-Paste Version

If you just want to copy-paste one command block:

```sql
USE ROLE ACCOUNTADMIN;
USE DATABASE TENDER_FOR_LAWYERS_DB;
USE SCHEMA VECTOR_SCHEMA;

CREATE TABLE IF NOT EXISTS agent_sessions (session_id VARCHAR(100) PRIMARY KEY, case_id VARCHAR(100) NOT NULL, agent_type VARCHAR(50), topic VARCHAR(500), status VARCHAR(20) DEFAULT 'active', created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(), last_activity TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(), message_count INT DEFAULT 0, completed_at TIMESTAMP_NTZ);

CREATE TABLE IF NOT EXISTS session_messages (message_id VARCHAR(100) PRIMARY KEY, session_id VARCHAR(100) NOT NULL, role VARCHAR(20) NOT NULL, content TEXT, timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP());

CREATE TABLE IF NOT EXISTS agent_activities (activity_id VARCHAR(100) PRIMARY KEY, case_id VARCHAR(100) NOT NULL, session_id VARCHAR(100), agent_type VARCHAR(50), agent_action VARCHAR(100), activity_status VARCHAR(20) DEFAULT 'pending', prompt TEXT, agent_response TEXT, action_data TEXT, requires_approval BOOLEAN DEFAULT FALSE, approved_by VARCHAR(200), approved_at TIMESTAMP_NTZ, execution_result TEXT, created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP());

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE agent_sessions TO ROLE TENDER_APP_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE session_messages TO ROLE TENDER_APP_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE agent_activities TO ROLE TENDER_APP_ROLE;

SELECT 'Setup complete! ✅' AS status;
```

---

**That's it!** After running this, your AI chatbot should work perfectly. 🚀
