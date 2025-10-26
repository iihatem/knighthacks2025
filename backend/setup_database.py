"""
Database Setup Script - Creates required tables for session management
Run this once to set up the database tables needed for the AI agent system
"""

import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

def get_snowflake_conn():
    """Establishes a connection to Snowflake."""
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )

def setup_tables():
    """Creates all required tables for session management"""
    
    print("🔧 Setting up database tables...")
    
    conn = get_snowflake_conn()
    cursor = conn.cursor()
    
    try:
        # 1. Create agent_sessions table
        print("\n📋 Creating agent_sessions table...")
        cursor.execute("""
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
            )
        """)
        print("✅ agent_sessions table created")
        
        # 2. Create session_messages table
        print("\n📋 Creating session_messages table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_messages (
                message_id VARCHAR(100) PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                role VARCHAR(20) NOT NULL,
                content TEXT,
                timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
        """)
        print("✅ session_messages table created")
        
        # 3. Create agent_activities table (if not exists)
        print("\n📋 Creating agent_activities table...")
        cursor.execute("""
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
            )
        """)
        print("✅ agent_activities table created")
        
        # 4. Create indexes
        print("\n🔍 Creating indexes...")
        
        indexes = [
            ("idx_sessions_case_id", "agent_sessions", "case_id"),
            ("idx_sessions_status", "agent_sessions", "status"),
            ("idx_messages_session_id", "session_messages", "session_id"),
            ("idx_activities_case_id", "agent_activities", "case_id"),
            ("idx_activities_session_id", "agent_activities", "session_id"),
            ("idx_activities_status", "agent_activities", "activity_status"),
        ]
        
        for idx_name, table_name, column_name in indexes:
            try:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {idx_name} 
                    ON {table_name}({column_name})
                """)
                print(f"✅ Index {idx_name} created")
            except Exception as e:
                print(f"⚠️  Index {idx_name} already exists or error: {e}")
        
        # 5. Verify tables
        print("\n🔍 Verifying tables...")
        cursor.execute("SHOW TABLES LIKE '%session%'")
        session_tables = cursor.fetchall()
        print(f"Found {len(session_tables)} session-related tables:")
        for table in session_tables:
            print(f"  - {table[1]}")  # table[1] is the table name
        
        cursor.execute("SHOW TABLES LIKE '%activities%'")
        activity_tables = cursor.fetchall()
        print(f"Found {len(activity_tables)} activity-related tables:")
        for table in activity_tables:
            print(f"  - {table[1]}")
        
        print("\n✅ Database setup complete!")
        print("\n📊 Summary:")
        print("  - agent_sessions: Tracks conversation sessions")
        print("  - session_messages: Stores all messages")
        print("  - agent_activities: Logs approval-needed actions")
        print("\n🚀 Your AI agent system is ready to use!")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI Agent System - Database Setup")
    print("=" * 60)
    
    try:
        setup_tables()
    except Exception as e:
        print(f"\n❌ Failed to connect to Snowflake: {e}")
        print("\n💡 Make sure your .env file has the correct Snowflake credentials:")
        print("   - SNOWFLAKE_USER")
        print("   - SNOWFLAKE_PASSWORD")
        print("   - SNOWFLAKE_ACCOUNT")
        print("   - SNOWFLAKE_WAREHOUSE")
        print("   - SNOWFLAKE_DATABASE")
        print("   - SNOWFLAKE_SCHEMA")
        print("   - SNOWFLAKE_ROLE")

