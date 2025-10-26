"""Orchestrator Agent - Main coordinator for legal case processing"""
import os
import google.generativeai as genai
from agents.orchistrator_agent.sub_agents.client_communication_agent.agent import client_communication_guru
from tools.salesforce_tools import salesforce_create_task, salesforce_update_case

def orchestrator(case_id: str, query: str, case_context: str = "") -> dict:
    """
    Main orchestrator that routes tasks to specialist agents
    
    Args:
        case_id: The case ID
        query: User's request
        case_context: RAG context about the case
    
    Returns:
        dict with response and proposed actions
    """
    
    # Configure Gemini
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Analyze the request
    analysis_prompt = f"""You are the Orchestrator for Morgan & Morgan legal AI system.

Case ID: {case_id}
Case Context: {case_context}
User Request: {query}

Analyze this request and determine:
1. What type of task is this? (client communication, case update, task creation)
2. Which action should be taken?

Respond in JSON format:
{{
  "task_type": "client_communication" or "case_update" or "create_task",
  "reasoning": "why this classification",
  "recommended_action": "what to do"
}}
"""

    analysis = model.generate_content(analysis_prompt)
    
    # Extract text from Gemini response
    analysis_text = analysis.candidates[0].content.parts[0].text
    
    # Route to appropriate specialist based on query
    if "email" in query.lower() or "message" in query.lower() or "update client" in query.lower():
        # Route to Client Communication Guru
        result = client_communication_guru(case_context, query)
        return {
            'status': 'success',
            'orchestrator_analysis': analysis_text,
            'delegated_to': 'ClientCommunicationGuru',
            'proposed_actions': [result]
        }
    
    elif "task" in query.lower() or "create" in query.lower():
        # Create Salesforce task
        task_result = salesforce_create_task(case_id, query, query)
        return {
            'status': 'success',
            'orchestrator_analysis': analysis_text,
            'action_taken': task_result
        }
    
    else:
        # Generic response
        return {
            'status': 'success',
            'orchestrator_analysis': analysis_text,
            'message': 'Request received. Please specify if you need email draft or task creation.'
        }
