-- ============================================
-- Session Management Tables Setup
-- ============================================
-- Run this in Snowflake to create the required tables for session management

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

-- 4. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sessions_case_id ON agent_sessions(case_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON agent_sessions(status);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON session_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_activities_case_id ON agent_activities(case_id);
CREATE INDEX IF NOT EXISTS idx_activities_session_id ON agent_activities(session_id);
CREATE INDEX IF NOT EXISTS idx_activities_status ON agent_activities(activity_status);

-- Verify tables were created
SHOW TABLES LIKE '%session%';
SHOW TABLES LIKE '%activities%';

SELECT 'Setup complete! Tables created successfully.' AS status;

