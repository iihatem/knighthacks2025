"""
Agent Activity Logger - Track all agent actions and approvals
"""
import uuid
from datetime import datetime
from app import get_snowflake_conn, app

def log_agent_activity(
    case_id: str,
    agent_type: str,
    agent_action: str,
    prompt: str,
    agent_response: str,
    action_data: dict = None,
    requires_approval: bool = True,
    session_id: str = None
) -> str:
    """
    Log a new agent activity to Snowflake
    
    Args:
        case_id: Case ID this activity belongs to
        agent_type: Type of agent (ClientCommunicationGuru, VoiceBotScheduler, etc.)
        agent_action: Specific action (draft_email, schedule_appointment, etc.)
        prompt: User's original request
        agent_response: What the agent proposed
        action_data: Agent-specific data (dict, will be stored as JSON)
        requires_approval: Whether this needs human approval
        session_id: Optional session ID to link this activity to a conversation
    
    Returns:
        activity_id: Unique ID for this activity
    """
    try:
        activity_id = f"act-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        conn = get_snowflake_conn()
        if not conn:
            app.logger.error("Failed to connect to Snowflake for activity logging")
            return None
        
        cursor = conn.cursor()
        
        try:
            # Convert action_data dict to JSON string for VARIANT column
            import json
            action_data_json = json.dumps(action_data) if action_data else None
            
            cursor.execute(
                """
                INSERT INTO agent_activities (
                    activity_id, case_id, agent_type, agent_action,
                    activity_status, prompt, agent_response, action_data, requires_approval, session_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, PARSE_JSON(%s), %s, %s)
                """,
                (
                    activity_id,
                    case_id,
                    agent_type,
                    agent_action,
                    'pending',
                    prompt,
                    agent_response,
                    action_data_json,
                    requires_approval,
                    session_id
                )
            )
            
            conn.commit()
            app.logger.info(f"✅ Logged activity {activity_id} for case {case_id}")
            return activity_id
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        app.logger.error(f"Error logging agent activity: {e}")
        return None


def get_case_activities(case_id: str, status: str = None):
    """
    Get all activities for a case, optionally filtered by status
    
    Args:
        case_id: Case ID to get activities for
        status: Optional filter ('pending', 'approved', 'rejected', 'completed')
    
    Returns:
        List of activity dicts, sorted by created_at DESC (newest first)
    """
    try:
        conn = get_snowflake_conn()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        try:
            if status:
                query = """
                    SELECT 
                        activity_id, case_id, agent_type, agent_action,
                        activity_status, prompt, agent_response, action_data,
                        created_at, updated_at, approved_at, approved_by,
                        requires_approval, execution_result, error_message
                    FROM agent_activities
                    WHERE case_id = %s AND activity_status = %s
                    ORDER BY created_at DESC
                """
                cursor.execute(query, (case_id, status))
            else:
                query = """
                    SELECT 
                        activity_id, case_id, agent_type, agent_action,
                        activity_status, prompt, agent_response, action_data,
                        created_at, updated_at, approved_at, approved_by,
                        requires_approval, execution_result, error_message
                    FROM agent_activities
                    WHERE case_id = %s
                    ORDER BY created_at DESC
                """
                cursor.execute(query, (case_id,))
            
            results = cursor.fetchall()
            
            activities = []
            for row in results:
                import json
                activities.append({
                    'activity_id': row[0],
                    'case_id': row[1],
                    'agent_type': row[2],
                    'agent_action': row[3],
                    'activity_status': row[4],
                    'prompt': row[5],
                    'agent_response': row[6],
                    'action_data': json.loads(row[7]) if row[7] else None,
                    'created_at': row[8].isoformat() if row[8] else None,
                    'updated_at': row[9].isoformat() if row[9] else None,
                    'approved_at': row[10].isoformat() if row[10] else None,
                    'approved_by': row[11],
                    'requires_approval': row[12],
                    'execution_result': row[13],
                    'error_message': row[14]
                })
            
            return activities
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        app.logger.error(f"Error getting case activities: {e}")
        return []


def update_activity_status(
    activity_id: str,
    status: str,
    approved_by: str = None,
    execution_result: str = None,
    error_message: str = None
):
    """
    Update an activity's status (approve, reject, mark as completed)
    
    Args:
        activity_id: Activity to update
        status: New status ('approved', 'rejected', 'completed', 'failed')
        approved_by: Email/name of person who approved/rejected
        execution_result: Result message after execution
        error_message: Error message if failed
    
    Returns:
        bool: Success status
    """
    try:
        conn = get_snowflake_conn()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                UPDATE agent_activities
                SET 
                    activity_status = %s,
                    updated_at = CURRENT_TIMESTAMP,
                    approved_at = CASE WHEN %s IN ('approved', 'rejected') THEN CURRENT_TIMESTAMP ELSE approved_at END,
                    approved_by = %s,
                    execution_result = %s,
                    error_message = %s
                WHERE activity_id = %s
                """,
                (status, status, approved_by, execution_result, error_message, activity_id)
            )
            
            conn.commit()
            app.logger.info(f"✅ Updated activity {activity_id} to status: {status}")
            return True
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        app.logger.error(f"Error updating activity status: {e}")
        return False


def get_pending_activities(case_id: str = None):
    """
    Get all pending activities, optionally for a specific case
    
    Args:
        case_id: Optional case ID to filter by
    
    Returns:
        List of pending activity dicts
    """
    if case_id:
        return get_case_activities(case_id, status='pending')
    else:
        # Get all pending activities across all cases
        try:
            conn = get_snowflake_conn()
            if not conn:
                return []
            
            cursor = conn.cursor()
            
            try:
                cursor.execute(
                    """
                    SELECT 
                        activity_id, case_id, agent_type, agent_action,
                        activity_status, prompt, agent_response, action_data,
                        created_at, requires_approval
                    FROM agent_activities
                    WHERE activity_status = 'pending'
                    ORDER BY created_at DESC
                    """
                )
                
                results = cursor.fetchall()
                
                activities = []
                import json
                for row in results:
                    activities.append({
                        'activity_id': row[0],
                        'case_id': row[1],
                        'agent_type': row[2],
                        'agent_action': row[3],
                        'activity_status': row[4],
                        'prompt': row[5],
                        'agent_response': row[6],
                        'action_data': json.loads(row[7]) if row[7] else None,
                        'created_at': row[8].isoformat() if row[8] else None,
                        'requires_approval': row[9]
                    })
                
                return activities
                
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            app.logger.error(f"Error getting pending activities: {e}")
            return []
