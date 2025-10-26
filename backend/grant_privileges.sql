-- ============================================
-- Grant Privileges for Session Management Tables
-- ============================================
-- Run this as ACCOUNTADMIN to grant privileges to your app role

USE ROLE ACCOUNTADMIN;
USE DATABASE TENDER_FOR_LAWYERS_DB;
USE SCHEMA VECTOR_SCHEMA;

-- Grant privileges on agent_sessions table
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE agent_sessions TO ROLE TENDER_APP_ROLE;

-- Grant privileges on session_messages table
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE session_messages TO ROLE TENDER_APP_ROLE;

-- Grant privileges on agent_activities table (if exists)
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE agent_activities TO ROLE TENDER_APP_ROLE;

-- Verify grants
SHOW GRANTS ON TABLE agent_sessions;
SHOW GRANTS ON TABLE session_messages;
SHOW GRANTS ON TABLE agent_activities;

SELECT 'Privileges granted successfully!' AS status;

