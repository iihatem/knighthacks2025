"""Orchestrator Agent - Main coordinator for legal case processing with session management"""
import os
import json
import google.generativeai as genai
from agents.orchistrator_agent.sub_agents.client_communication_agent.agent import client_communication_guru
from agents.orchistrator_agent.sub_agents.evidence_sorter_agent.agent import evidence_sorter_guru
from agents.orchistrator_agent.sub_agents.records_wrangler_agent.agent import records_wrangler_guru
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
- process_evidence: Process email attachments and categorize evidence (NO APPROVAL)
- search_records: Search for existing case records in storage (NO APPROVAL)
- request_records: Draft email to request missing records from providers (REQUIRES APPROVAL)
- general_query: General question, analysis (NO APPROVAL)

Respond in JSON format:
{{
  "is_continuation": true or false,
  "topic": "Brief description of topic",
  "action_type": "research_internal|research_external|draft_email|schedule_appointment|process_evidence|search_records|request_records|general_query",
  "agent_type": "LegalResearcher|ClientCommunicationGuru|VoiceBotScheduler|EvidenceSorter|RecordsWrangler|Orchestrator",
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
        # Route to Client Communication Guru with case_id and session_id
        # send_email=True will actually send the email via SMTP after logging
        agent_response = client_communication_guru(
            case_context=case_context, 
            task=query, 
            case_id=case_id,
            session_id=current_session,
            send_email=True  # Actually send the email to client
        )
        
        # Activity is already logged by email_sender if email was sent
        # If email was not sent (just drafted), log it here
        if not agent_response.get('email_sent', False):
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
        else:
            # Email was sent - activity_id comes from email_sender
            activity_id = agent_response.get('activity_id')
        
        # Prepare response message
        if agent_response.get('email_sent'):
            response_message = f"✅ Email sent to {agent_response.get('to_name')} ({agent_response.get('to')})\n\n{agent_response.get('draft', 'Email drafted')}"
        else:
            response_message = f"⚠️ Email drafted but not sent: {agent_response.get('send_message', 'Unknown error')}\n\n{agent_response.get('draft', 'Email drafted')}"
    
    elif action_type == 'process_evidence':
        # Route to Evidence Sorter - processes email attachments
        # Extract attachments from query context (would come from frontend)
        agent_response = evidence_sorter_guru(
            case_id=case_id,
            query=query,
            attachments=[]  # Attachments should come from frontend
        )
        
        # Activity is already logged by evidence_processor
        activity_id = agent_response.get('activity_id')
        response_message = agent_response.get('message', 'Evidence processed successfully')
    
    elif action_type == 'search_records':
        # Route to Records Wrangler - search for existing records
        agent_response = records_wrangler_guru(
            case_id=case_id,
            query=query,
            action_type='search_records'
        )
        
        # NO activity log - search doesn't require approval
        response_message = agent_response.get('message', 'Records search completed')
    
    elif action_type == 'request_records':
        # Route to Records Wrangler - draft request email to provider
        agent_response = records_wrangler_guru(
            case_id=case_id,
            query=query,
            action_type='request_records'
        )
        
        # REQUIRES APPROVAL - Log activity
        if agent_response.get('draft'):
            activity_id = log_agent_activity(
                case_id=case_id,
                agent_type='RecordsWrangler',
                agent_action='request_records',
                prompt=query,
                agent_response=json.dumps(agent_response.get('draft')),
                action_data={
                    'draft': agent_response.get('draft'),
                    'to': agent_response.get('draft', {}).get('to', 'Unknown provider'),
                    'subject': agent_response.get('draft', {}).get('subject', 'Records Request')
                },
                requires_approval=True,
                session_id=current_session
            )
        
        response_message = agent_response.get('message', 'Records request email drafted')
        
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
        
    elif action_type == 'research_external':
        # Legal Research with web search - NO APPROVAL NEEDED
        from agents.orchistrator_agent.sub_agents.legal_researcher_agent.agent import legal_researcher
        
        agent_response = legal_researcher(case_id, query, case_context)
        
        # NO activity log - research doesn't require approval, just stored in session
        response_message = agent_response.get('summary', 'Legal research completed')
        
    elif action_type == 'research_internal':
        # Internal RAG search - NO APPROVAL NEEDED
        # Use the case_context that was already retrieved via RAG
        if case_context and len(case_context.strip()) > 0:
            # Generate a comprehensive answer using the RAG context
            research_prompt = f"""You are a legal research assistant. Based on the case files provided below, answer the user's question comprehensively.

Case Files Context:
{case_context}

User Question: {query}

Provide a detailed answer based on the case files. If the information is not in the case files, clearly state that.
"""
            research_response = model.generate_content(research_prompt)
            research_answer = research_response.candidates[0].content.parts[0].text
            
            agent_response = {
                'action_type': action_type,
                'message': research_answer,
                'context_found': True,
                'query': query
            }
            response_message = research_answer
        else:
            # No context found
            agent_response = {
                'action_type': action_type,
                'message': "I couldn't find relevant information in the case files for this query.",
                'context_found': False,
                'query': query
            }
            response_message = "I couldn't find relevant information in the case files for this query."
        
        # NO activity log - just store in session
        
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
