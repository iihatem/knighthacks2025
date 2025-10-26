"""
Session Management Service
Handles conversation sessions between users and AI agents
"""

import secrets
from datetime import datetime
from flask import current_app as app


def get_snowflake_conn():
    """Import from main app to avoid circular imports"""
    from app import get_snowflake_conn as get_conn
    return get_conn()


def create_session(case_id: str, agent_type: str, topic: str) -> str:
    """
    Create a new conversation session
    
    Args:
        case_id: The case this session belongs to
        agent_type: Which agent is handling this (LegalResearcher, ClientCommunicationGuru, etc.)
        topic: Brief description of what this session is about
    
    Returns:
        session_id: Unique identifier for this session
    """
    try:
        # Generate session ID: sess-YYYYMMDD-random
        session_id = f"sess-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4)}"
        
        conn = get_snowflake_conn()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO agent_sessions (
            session_id, case_id, agent_type, topic, status, 
            created_at, last_activity, message_count
        ) VALUES (
            %s, %s, %s, %s, 'active', 
            CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0
        )
        """
        
        cursor.execute(query, (session_id, case_id, agent_type, topic))
        conn.commit()
        cursor.close()
        
        app.logger.info(f"Created session {session_id} for case {case_id}")
        return session_id
        
    except Exception as e:
        app.logger.error(f"Error creating session: {e}")
        raise


def get_active_session(case_id: str, agent_type: str = None) -> dict:
    """
    Get the most recent active session for a case
    
    Args:
        case_id: The case to check
        agent_type: Optional - filter by specific agent type
    
    Returns:
        Session data or None if no active session
    """
    try:
        conn = get_snowflake_conn()
        cursor = conn.cursor()
        
        if agent_type:
            query = """
            SELECT session_id, case_id, agent_type, topic, status, 
                   created_at, last_activity, message_count
            FROM agent_sessions
            WHERE case_id = %s AND agent_type = %s AND status = 'active'
            ORDER BY last_activity DESC
            LIMIT 1
            """
            cursor.execute(query, (case_id, agent_type))
        else:
            query = """
            SELECT session_id, case_id, agent_type, topic, status, 
                   created_at, last_activity, message_count
            FROM agent_sessions
            WHERE case_id = %s AND status = 'active'
            ORDER BY last_activity DESC
            LIMIT 1
            """
            cursor.execute(query, (case_id,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                'session_id': result[0],
                'case_id': result[1],
                'agent_type': result[2],
                'topic': result[3],
                'status': result[4],
                'created_at': result[5].isoformat() if result[5] else None,
                'last_activity': result[6].isoformat() if result[6] else None,
                'message_count': result[7]
            }
        return None
        
    except Exception as e:
        app.logger.error(f"Error getting active session: {e}")
        return None


def store_message(session_id: str, role: str, content: str) -> str:
    """
    Store a message in a session
    
    Args:
        session_id: The session this message belongs to
        role: 'user' or 'agent'
        content: The message content
    
    Returns:
        message_id: Unique identifier for this message
    """
    try:
        # Generate message ID
        message_id = f"msg-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3)}"
        
        conn = get_snowflake_conn()
        cursor = conn.cursor()
        
        # Insert message
        query = """
        INSERT INTO session_messages (message_id, session_id, role, content, timestamp)
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP())
        """
        cursor.execute(query, (message_id, session_id, role, content))
        
        # Update session's last_activity and message_count
        update_query = """
        UPDATE agent_sessions
        SET last_activity = CURRENT_TIMESTAMP(),
            message_count = message_count + 1
        WHERE session_id = %s
        """
        cursor.execute(update_query, (session_id,))
        
        conn.commit()
        cursor.close()
        
        return message_id
        
    except Exception as e:
        app.logger.error(f"Error storing message: {e}")
        raise


def get_session_messages(session_id: str, limit: int = 50) -> list:
    """
    Get all messages from a session
    
    Args:
        session_id: The session to retrieve messages from
        limit: Maximum number of messages to return (default 50)
    
    Returns:
        List of messages with role and content
    """
    try:
        conn = get_snowflake_conn()
        cursor = conn.cursor()
        
        query = """
        SELECT message_id, role, content, timestamp
        FROM session_messages
        WHERE session_id = %s
        ORDER BY timestamp ASC
        LIMIT %s
        """
        
        cursor.execute(query, (session_id, limit))
        results = cursor.fetchall()
        cursor.close()
        
        messages = []
        for row in results:
            messages.append({
                'message_id': row[0],
                'role': row[1],
                'content': row[2],
                'timestamp': row[3].isoformat() if row[3] else None
            })
        
        return messages
        
    except Exception as e:
        app.logger.error(f"Error getting session messages: {e}")
        return []


def get_recent_messages(session_id: str, count: int = 5) -> list:
    """
    Get the most recent N messages from a session
    
    Args:
        session_id: The session to retrieve from
        count: Number of recent messages (default 5)
    
    Returns:
        List of recent messages
    """
    try:
        conn = get_snowflake_conn()
        cursor = conn.cursor()
        
        query = """
        SELECT role, content
        FROM session_messages
        WHERE session_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
        """
        
        cursor.execute(query, (session_id, count))
        results = cursor.fetchall()
        cursor.close()
        
        # Reverse to get chronological order (oldest to newest)
        messages = [{'role': row[0], 'content': row[1]} for row in reversed(results)]
        return messages
        
    except Exception as e:
        app.logger.error(f"Error getting recent messages: {e}")
        return []


def end_session(session_id: str, status: str = 'completed') -> bool:
    """
    Mark a session as completed
    
    Args:
        session_id: The session to end
        status: Final status ('completed' or 'needs_approval')
    
    Returns:
        True if successful
    """
    try:
        conn = get_snowflake_conn()
        cursor = conn.cursor()
        
        query = """
        UPDATE agent_sessions
        SET status = %s, completed_at = CURRENT_TIMESTAMP()
        WHERE session_id = %s
        """
        
        cursor.execute(query, (status, session_id))
        conn.commit()
        cursor.close()
        
        app.logger.info(f"Ended session {session_id} with status {status}")
        return True
        
    except Exception as e:
        app.logger.error(f"Error ending session: {e}")
        return False


def get_case_sessions(case_id: str, status: str = None) -> list:
    """
    Get all sessions for a case
    
    Args:
        case_id: The case to retrieve sessions for
        status: Optional status filter
    
    Returns:
        List of sessions
    """
    try:
        conn = get_snowflake_conn()
        cursor = conn.cursor()
        
        if status:
            query = """
            SELECT session_id, agent_type, topic, status, 
                   created_at, last_activity, message_count
            FROM agent_sessions
            WHERE case_id = %s AND status = %s
            ORDER BY last_activity DESC
            """
            cursor.execute(query, (case_id, status))
        else:
            query = """
            SELECT session_id, agent_type, topic, status, 
                   created_at, last_activity, message_count
            FROM agent_sessions
            WHERE case_id = %s
            ORDER BY last_activity DESC
            """
            cursor.execute(query, (case_id,))
        
        results = cursor.fetchall()
        cursor.close()
        
        sessions = []
        for row in results:
            sessions.append({
                'session_id': row[0],
                'agent_type': row[1],
                'topic': row[2],
                'status': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
                'last_activity': row[5].isoformat() if row[5] else None,
                'message_count': row[6]
            })
        
        return sessions
        
    except Exception as e:
        app.logger.error(f"Error getting case sessions: {e}")
        return []
