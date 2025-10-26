"""
Fix Privileges Script - Grants necessary privileges to tables
Run this to fix the privilege issues with session management tables
"""

import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

def get_snowflake_conn_as_admin():
    """Establishes a connection to Snowflake as ACCOUNTADMIN."""
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role="ACCOUNTADMIN"  # Use ACCOUNTADMIN to grant privileges
    )

def grant_privileges():
    """Grants necessary privileges to the app role"""
    
    print("🔧 Granting privileges to session management tables...")
    
    try:
        conn = get_snowflake_conn_as_admin()
        cursor = conn.cursor()
        
        app_role = os.getenv("SNOWFLAKE_ROLE", "TENDER_APP_ROLE")
        
        tables = ["agent_sessions", "session_messages", "agent_activities"]
        
        for table in tables:
            print(f"\n📋 Granting privileges on {table}...")
            try:
                cursor.execute(f"""
                    GRANT SELECT, INSERT, UPDATE, DELETE 
                    ON TABLE {table} 
                    TO ROLE {app_role}
                """)
                print(f"✅ Privileges granted on {table}")
            except Exception as e:
                print(f"⚠️  Error granting privileges on {table}: {e}")
        
        print("\n✅ Privilege grant complete!")
        print(f"\n🚀 Role {app_role} now has access to session management tables!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 This script needs to run as ACCOUNTADMIN.")
        print("   Make sure your Snowflake user has ACCOUNTADMIN privileges.")

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 AI Agent System - Fix Table Privileges")
    print("=" * 60)
    
    grant_privileges()

