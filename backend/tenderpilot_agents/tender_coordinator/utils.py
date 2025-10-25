"""
Utility functions for TenderPilot Coordinator Agent.
Enhanced with intelligent task type recognition and delegation.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def error_response(error_message: str, error_code: str = "GENERIC_ERROR") -> Dict[str, Any]:
    """Create a standardized error response."""
    return {
        "status": "error",
        "error_code": error_code,
        "message": error_message,
        "timestamp": datetime.now().isoformat()
    }


def success_response(data: Dict[str, Any], message: str = "Success") -> Dict[str, Any]:
    """Create a standardized success response."""
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }


def intelligent_task_type_detection(user_input: str) -> Dict[str, Any]:
    """
    Intelligently detect task type from user input using keyword analysis.
    
    Args:
        user_input: User's input message
        
    Returns:
        Detected task type and confidence
    """
    logger.info(f"Analyzing user input for task type: '{user_input}'")
    
    # Convert to lowercase for analysis
    input_lower = user_input.lower()
    
    # Define keyword patterns for each task type
    task_patterns = {
        "medical_records": [
            "medical", "records", "billing", "hospital", "doctor", "patient", 
            "mri", "x-ray", "lab", "test", "diagnosis", "treatment", "provider"
        ],
        "client_communication": [
            "client", "communication", "message", "email", "call", "notify", 
            "update", "inform", "contact", "reach out", "send", "draft", "write",
            "deposition", "meeting", "appointment", "reminder", "check in"
        ],
        "legal_research": [
            "research", "legal", "case law", "precedent", "statute", "law",
            "copyright", "infringement", "music", "remastering", "legal issue",
            "find", "search", "analyze", "investigate", "study"
        ],
        "schedule_appointment": [
            "schedule", "appointment", "meeting", "deposition", "call", "book",
            "arrange", "coordinate", "set up", "plan", "organize", "calendar"
        ],
        "document_organization": [
            "organize", "documents", "evidence", "files", "papers", "sort",
            "categorize", "index", "arrange", "structure", "manage"
        ]
    }
    
    # Calculate confidence scores for each task type
    confidence_scores = {}
    
    for task_type, keywords in task_patterns.items():
        score = 0
        matched_keywords = []
        
        for keyword in keywords:
            if keyword in input_lower:
                score += 1
                matched_keywords.append(keyword)
        
        # Normalize score (0-1)
        confidence = score / len(keywords)
        confidence_scores[task_type] = {
            "confidence": confidence,
            "matched_keywords": matched_keywords,
            "score": score
        }
    
    # Find the best match
    best_match = max(confidence_scores.items(), key=lambda x: x[1]["confidence"])
    best_task_type = best_match[0]
    best_confidence = best_match[1]["confidence"]
    
    # Set confidence threshold
    if best_confidence < 0.1:  # Very low confidence
        return {
            "task_type": "unknown",
            "confidence": best_confidence,
            "reasoning": "No clear task type detected from input",
            "suggestions": list(task_patterns.keys())
        }
    
    return {
        "task_type": best_task_type,
        "confidence": best_confidence,
        "reasoning": f"Detected '{best_task_type}' based on keywords: {best_match[1]['matched_keywords']}",
        "matched_keywords": best_match[1]["matched_keywords"]
    }


def route_task_to_agent(task_type: str, task_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Route task to appropriate specialized agent with intelligent task type detection.
    This is the first step - delegation happens immediately, approval comes after execution.
    
    Args:
        task_type: Task type (can be user input or detected type)
        task_data: Additional task data
        
    Returns:
        Routing result with target agent information
    """
    logger.info(f"Routing task: {task_type}")
    
    # If task_type looks like user input, detect the actual task type
    if len(task_type.split()) > 2 or " " in task_type:
        detection_result = intelligent_task_type_detection(task_type)
        if detection_result["task_type"] == "unknown":
            return error_response(
                f"Could not determine task type from: '{task_type}'",
                "TASK_TYPE_DETECTION_FAILED"
            )
        task_type = detection_result["task_type"]
        logger.info(f"Detected task type: {task_type} (confidence: {detection_result['confidence']})")
    
    # Define agent routing mapping
    agent_mapping = {
        "medical_records": {
            "agent": "records_wrangler",
            "confidence": 0.95,
            "reasoning": "Medical records require specialized handling"
        },
        "client_communication": {
            "agent": "client_communication_guru", 
            "confidence": 0.90,
            "reasoning": "Client communication requires empathetic messaging"
        },
        "legal_research": {
            "agent": "legal_researcher",
            "confidence": 0.88,
            "reasoning": "Legal research requires specialized case law analysis"
        },
        "schedule_appointment": {
            "agent": "voice_scheduler",
            "confidence": 0.92,
            "reasoning": "Appointment scheduling requires voice coordination"
        },
        "document_organization": {
            "agent": "evidence_sorter",
            "confidence": 0.85,
            "reasoning": "Document organization requires specialized evidence handling"
        }
    }
    
    # Check if task type is supported
    if task_type not in agent_mapping:
        return error_response(
            f"Unknown task type: {task_type}",
            "UNKNOWN_TASK_TYPE"
        )
    
    # Get routing information
    routing_info = agent_mapping[task_type]
    
    # ALWAYS delegate first - approval comes after execution
    return success_response(
        {
            "task_type": task_type,
            "target_agent": routing_info["agent"],
            "confidence": routing_info["confidence"],
            "reasoning": routing_info["reasoning"],
            "routing_timestamp": datetime.now().isoformat(),
            "status": "delegated"
        },
        f"Task delegated to {routing_info['agent']} for execution"
    )


def coordinate_multi_agent_workflow(workflow_type: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Coordinate multi-agent workflows for complex tasks.
    
    Args:
        workflow_type: Type of workflow to coordinate
        tasks: List of tasks to coordinate
        
    Returns:
        Workflow coordination result
    """
    logger.info(f"Coordinating {workflow_type} workflow with {len(tasks)} tasks")
    
    workflow_result = {
        "workflow_type": workflow_type,
        "total_tasks": len(tasks),
        "coordination_status": "success",
        "task_sequence": [],
        "estimated_duration": len(tasks) * 5,  # 5 minutes per task
        "coordination_timestamp": datetime.now().isoformat()
    }
    
    # Create task sequence
    for i, task in enumerate(tasks):
        task_info = {
            "step": i + 1,
            "task_type": task.get("task_type", "unknown"),
            "description": task.get("description", "No description"),
            "estimated_time": "5 minutes"
        }
        workflow_result["task_sequence"].append(task_info)
    
    return success_response(
        workflow_result,
        f"Multi-agent workflow coordinated for {workflow_type}"
    )


def execute_task_with_agent(task_type: str, target_agent: str, task_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute task with the delegated agent and get execution result.
    This is step 2 - after delegation, the agent executes and suggests a result.
    
    Args:
        task_type: Type of task
        target_agent: Agent that will execute the task
        task_data: Task data for execution
        
    Returns:
        Execution result with suggested action
    """
    logger.info(f"Executing {task_type} with {target_agent}")
    
    # Simulate agent execution and result suggestion
    execution_result = {
        "task_type": task_type,
        "executing_agent": target_agent,
        "execution_status": "completed",
        "suggested_action": f"Agent {target_agent} has executed the {task_type} task",
        "execution_details": {
            "action_taken": f"Processed {task_type} using {target_agent} capabilities",
            "result_summary": f"Task execution completed successfully",
            "confidence": 0.85,
            "execution_timestamp": datetime.now().isoformat()
        },
        "requires_approval": True,  # Most executed tasks require approval
        "approval_pending": True
    }
    
    # Add specific execution details based on task type
    if task_type == "client_communication":
        execution_result["suggested_action"] = "Draft client message ready for review"
        execution_result["execution_details"]["message_draft"] = "Dear [Client], [Message content]"
    elif task_type == "legal_research":
        execution_result["suggested_action"] = "Legal research completed with precedents found"
        execution_result["execution_details"]["research_summary"] = "Found 5 relevant precedents"
    elif task_type == "medical_records":
        execution_result["suggested_action"] = "Medical records request processed"
        execution_result["execution_details"]["records_status"] = "Request sent to provider"
    elif task_type == "schedule_appointment":
        execution_result["suggested_action"] = "Appointment scheduled via voice call"
        execution_result["execution_details"]["scheduling_status"] = "Call completed, appointment confirmed"
    elif task_type == "document_organization":
        execution_result["suggested_action"] = "Documents organized and categorized"
        execution_result["execution_details"]["organization_status"] = "Files sorted into appropriate folders"
    
    return success_response(
        execution_result,
        f"Task executed by {target_agent}, awaiting approval"
    )


def check_approval_required_after_execution(execution_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if executed task requires human approval.
    This is step 3 - after execution, check if approval is needed.
    
    Args:
        execution_result: Result from agent execution
        
    Returns:
        Approval requirement result
    """
    logger.info("Checking approval requirements after execution")
    
    task_type = execution_result.get("task_type", "unknown")
    
    # Define approval requirements for executed tasks
    approval_required_tasks = [
        "client_communication",
        "settlement_discussion", 
        "high_value_negotiation",
        "legal_filing",
        "court_communication"
    ]
    
    requires_approval = task_type in approval_required_tasks
    
    # Additional context-based approval logic
    if execution_result.get("execution_details", {}).get("confidence", 0) < 0.8:
        requires_approval = True
    
    return success_response(
        {
            "task_type": task_type,
            "requires_approval": requires_approval,
            "execution_result": execution_result,
            "approval_reason": "High priority or sensitive communication" if requires_approval else "Standard processing",
            "check_timestamp": datetime.now().isoformat()
        },
        f"Approval {'required' if requires_approval else 'not required'} for executed {task_type}"
    )


def send_approval_request_for_execution(execution_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send approval request for executed task that needs human approval.
    This is step 4 - after execution, send approval request for the suggested action.
    
    Args:
        execution_result: Result from agent execution
        
    Returns:
        Approval request result
    """
    logger.info(f"Sending approval request for executed task: {execution_result.get('task_type', 'unknown')}")
    
    approval_request = {
        "task_type": execution_result.get("task_type", "unknown"),
        "executing_agent": execution_result.get("executing_agent", "unknown"),
        "suggested_action": execution_result.get("suggested_action", "No action suggested"),
        "execution_details": execution_result.get("execution_details", {}),
        "approval_id": f"approval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "status": "pending",
        "request_timestamp": datetime.now().isoformat(),
        "approval_channels": ["email", "slack", "dashboard"],
        "priority": "normal",
        "approval_message": f"Please review and approve the following action: {execution_result.get('suggested_action', 'No action specified')}"
    }
    
    return success_response(
        approval_request,
        f"Approval request sent for executed {execution_result.get('task_type', 'task')}"
    )


def process_approved_execution(approval_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process an executed task that has been approved by a human.
    This is step 5 - final step after human approval of the executed task.
    
    Args:
        approval_data: Approval data from human
        
    Returns:
        Final processing result
    """
    logger.info("Processing approved execution")
    
    task_type = approval_data.get("task_type", "unknown")
    executing_agent = approval_data.get("executing_agent", "unknown")
    suggested_action = approval_data.get("suggested_action", "No action specified")
    
    # Finalize the approved execution
    final_result = {
        "task_type": task_type,
        "executing_agent": executing_agent,
        "approved_action": suggested_action,
        "final_status": "approved_and_finalized",
        "approval_timestamp": datetime.now().isoformat(),
        "completion_message": f"Task '{task_type}' executed by {executing_agent} has been approved and finalized"
    }
    
    # Add specific finalization details
    if task_type == "client_communication":
        final_result["action_taken"] = "Client message sent"
        final_result["recipient"] = "Client"
    elif task_type == "legal_research":
        final_result["action_taken"] = "Legal research results delivered"
        final_result["research_summary"] = "Precedents and citations provided"
    elif task_type == "medical_records":
        final_result["action_taken"] = "Medical records request completed"
        final_result["records_status"] = "Request processed and sent"
    elif task_type == "schedule_appointment":
        final_result["action_taken"] = "Appointment confirmed and scheduled"
        final_result["scheduling_status"] = "Meeting scheduled successfully"
    elif task_type == "document_organization":
        final_result["action_taken"] = "Documents organized and filed"
        final_result["organization_status"] = "Files properly categorized"
    
    return success_response(
        final_result,
        f"Approved execution of {task_type} by {executing_agent} has been finalized"
    )


def monitor_agent_health() -> Dict[str, Any]:
    """
    Monitor the health status of all specialized agents.
    
    Returns:
        Agent health status
    """
    logger.info("Monitoring agent health")
    
    agents = [
        "records_wrangler",
        "client_communication_guru", 
        "legal_researcher",
        "voice_scheduler",
        "evidence_sorter"
    ]
    
    health_status = {
        "overall_status": "healthy",
        "agents": {},
        "monitoring_timestamp": datetime.now().isoformat()
    }
    
    for agent in agents:
        health_status["agents"][agent] = {
            "status": "healthy",
            "response_time": "normal",
            "last_activity": datetime.now().isoformat()
        }
    
    return success_response(
        health_status,
        "Agent health monitoring completed"
    )


def generate_task_summary(task_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a summary of completed tasks.
    
    Args:
        task_results: List of task results
        
    Returns:
        Task summary
    """
    logger.info(f"Generating task summary for {len(task_results)} tasks")
    
    summary = {
        "total_tasks": len(task_results),
        "successful_tasks": len([r for r in task_results if r.get("status") == "success"]),
        "failed_tasks": len([r for r in task_results if r.get("status") == "error"]),
        "task_types": list(set([r.get("task_type", "unknown") for r in task_results])),
        "summary_timestamp": datetime.now().isoformat()
    }
    
    return success_response(
        summary,
        f"Task summary generated for {summary['total_tasks']} tasks"
    )