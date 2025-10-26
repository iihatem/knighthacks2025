"""Salesforce CRM integration tools"""
from datetime import datetime, timedelta
from services.salesforce_service import get_salesforce_client

def salesforce_create_task(case_id: str, subject: str, description: str = "", 
                          priority: str = "Normal", due_days: int = 7) -> str:
    """
    Create a task in Salesforce linked to a case
    
    Args:
        case_id: Salesforce Case ID
        subject: Task subject line
        description: Task description
        priority: "High", "Normal", or "Low"
        due_days: Days until due (default 7)
    
    Returns:
        Success message with Task ID or error message
    """
    try:
        sf = get_salesforce_client()
        
        due_date = (datetime.now() + timedelta(days=due_days)).strftime('%Y-%m-%d')
        
        task_data = {
            'Subject': subject,
            'Description': description,
            'WhatId': case_id,  # Links to Case
            'Status': 'Not Started',
            'Priority': priority,
            'ActivityDate': due_date
        }
        
        result = sf.Task.create(task_data)
        
        if result.get('success'):
            return f"✅ Task created: {result['id']}"
        else:
            return f"❌ Failed to create task: {result.get('errors')}"
            
    except Exception as e:
        return f"❌ Error creating task: {str(e)}"


def salesforce_update_case(case_id: str, status: str = None, 
                          description: str = None) -> str:
    """
    Update a Salesforce case
    
    Args:
        case_id: Salesforce Case ID
        status: New status ("New", "Working", "Escalated", "Closed")
        description: Additional notes to append
    
    Returns:
        Success message or error message
    """
    try:
        sf = get_salesforce_client()
        
        update_data = {}
        if status:
            update_data['Status'] = status
        if description:
            update_data['Description'] = description
            
        if not update_data:
            return "⚠️ No updates provided"
        
        result = sf.Case.update(case_id, update_data)
        
        if result == 204:  # Salesforce returns 204 for successful update
            return f"✅ Case {case_id} updated successfully"
        else:
            return f"❌ Update failed with status: {result}"
            
    except Exception as e:
        return f"❌ Error updating case: {str(e)}"
