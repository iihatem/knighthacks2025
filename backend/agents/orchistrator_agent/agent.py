"""Orchestrator Agent - Main coordinator for legal case processing with session management"""
import os
import json
import google.generativeai as genai
from agents.orchistrator_agent.sub_agents.client_communication_agent.agent import client_communication_guru
from tools.salesforce_tools import salesforce_create_task, salesforce_update_case
from services.activity_logger import log_agent_activity
from services.session_manager import (
    create_session, get_active_session, store_message, 
    get_recent_messages, end_session
)

def orchestrator(case_id: str, query: str, case_context: str = "", session_id: str = None) -> dict:
    """
    Main orchestrator that routes tasks to specialist agents with smart session management
    
    Args:
        case_id: The case ID
        query: User's request
        case_context: RAG context about the case
        session_id: Optional existing session ID to continue
    
    Returns:
        dict with response, session info, and proposed actions
    """
    
    # Configure Gemini
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Step 1: Check for existing session or get recent context
    recent_messages = []
    current_session = None
    
    if session_id:
        # User provided session - continue it
        recent_messages = get_recent_messages(session_id, count=5)
        current_session = session_id
    else:
        # Check if there's an active session for this case
        active_session = get_active_session(case_id)
        if active_session:
            current_session = active_session['session_id']
            recent_messages = get_recent_messages(current_session, count=5)
    
    # Step 2: Analyze if this is a new topic or continuation
    context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
    
    session_analysis_prompt = f"""You are analyzing a conversation to determine session continuity and required actions.

Recent conversation history (last 5 messages):
{context_text if context_text else "No previous conversation"}

New user message: "{query}"

Case Context: {case_context}

Determine:
1. Is this a CONTINUATION of previous conversation or a NEW topic?
2. What is the main topic/intent?
3. What action type is needed?
4. Does this action require approval before execution?

Action types:
- research_internal: Search case files in RAG database (NO APPROVAL)
- research_external: Web search, case law databases (NO APPROVAL)  
- draft_email: Draft email to client/opposing counsel (REQUIRES APPROVAL)
- schedule_appointment: Schedule deposition/mediation (REQUIRES APPROVAL)
- general_query: General question, analysis (NO APPROVAL)

Respond in JSON format:
{{
  "is_continuation": true or false,
  "topic": "Brief description of topic",
  "action_type": "research_internal|research_external|draft_email|schedule_appointment|general_query",
  "agent_type": "LegalResearcher|ClientCommunicationGuru|VoiceBotScheduler|Orchestrator",
  "requires_approval": true or false,
  "reasoning": "Why you made this determination"
}}
"""

    analysis = model.generate_content(session_analysis_prompt)
    analysis_text = analysis.candidates[0].content.parts[0].text
    
    # Parse the analysis
    try:
        analysis_data = json.loads(analysis_text)
    except:
        # Fallback if JSON parsing fails
        analysis_data = {
            "is_continuation": False,
            "topic": "General query",
            "action_type": "general_query",
            "agent_type": "Orchestrator",
            "requires_approval": False,
            "reasoning": "Failed to parse, defaulting to safe general query"
        }
    
    # Step 3: Session management decision
    session_mode = 'continue'
    
    if current_session and analysis_data.get('is_continuation', False):
        # Continue existing session
        session_mode = 'continue'
    else:
        # Start new session
        session_mode = 'new'
        current_session = create_session(
            case_id=case_id,
            agent_type=analysis_data.get('agent_type', 'Orchestrator'),
            topic=analysis_data.get('topic', 'General query')
        )
    
    # Step 4: Store user message in session
    store_message(current_session, 'user', query)
    
    # Step 5: Route to appropriate agent based on action_type
    action_type = analysis_data.get('action_type', 'general_query')
    agent_response = None
    activity_id = None
    
    if action_type == 'draft_email':
        # Route to Client Communication Guru
        agent_response = client_communication_guru(case_context, query)
        
        # REQUIRES APPROVAL - Log activity immediately
        activity_id = log_agent_activity(
            case_id=case_id,
            agent_type='ClientCommunicationGuru',
            agent_action='draft_email',
            prompt=query,
            agent_response=json.dumps(agent_response),
            action_data={
                'draft': agent_response.get('draft', ''),
                'to': agent_response.get('to', 'Unknown client'),
                'subject': agent_response.get('subject', 'Case Update')
            },
            requires_approval=True,
            session_id=current_session
        )
        
        response_message = agent_response.get('draft', 'Email drafted')
        
    elif action_type == 'schedule_appointment':
        # Placeholder for VoiceBotScheduler (to be implemented)
        agent_response = {
            'message': 'Appointment scheduling requested',
            'note': 'VoiceBotScheduler agent not yet implemented'
        }
        
        # REQUIRES APPROVAL - Log activity
        activity_id = log_agent_activity(
            case_id=case_id,
            agent_type='VoiceBotScheduler',
            agent_action='schedule_appointment',
            prompt=query,
            agent_response=json.dumps(agent_response),
            action_data={'request': query},
            requires_approval=True,
            session_id=current_session
        )
        
        response_message = "Appointment scheduling requires approval (agent not yet implemented)"
        
    elif action_type in ['research_internal', 'research_external']:
        # Research - NO APPROVAL NEEDED
        # For now, return a helpful message
        agent_response = {
            'action_type': action_type,
            'message': f'Conducting {action_type.replace("_", " ")}...',
            'note': 'Research agents process queries without approval',
            'query': query
        }
        
        # NO activity log - just store in session
        response_message = f"Researching: {query}"
        
    else:
        # General query - NO APPROVAL NEEDED
        agent_response = {
            'message': 'Query processed',
            'analysis': analysis_data.get('reasoning', 'General inquiry')
        }
        
        response_message = "I'm here to help. You can ask me to research cases, draft emails, or schedule appointments."
    
    # Step 6: Store agent response in session
    store_message(current_session, 'agent', json.dumps(agent_response))
    
    # Step 7: Build response
    return {
        'status': 'success',
        'session_id': current_session,
        'session_mode': session_mode,  # 'new' or 'continue'
        'topic': analysis_data.get('topic'),
        'action_type': action_type,
        'requires_approval': analysis_data.get('requires_approval', False),
        'activity_id': activity_id,  # Only set if approval needed
        'agent_type': analysis_data.get('agent_type'),
        'message': response_message,
        'agent_response': agent_response,
        'reasoning': analysis_data.get('reasoning')
    }
