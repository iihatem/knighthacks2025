"""Voice Scheduler Agent - Appointment coordination specialist"""
import os
import json
import logging
from typing import Any, Dict

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class VoiceSchedulerAgent:
    """Agent for appointment coordination and scheduling"""
    
    SYSTEM_INSTRUCTION = """You are a Voice Scheduler Agent specializing in appointment coordination.

Your primary responsibilities include:

1. CLIENT COMMUNICATION:
   - Coordinate with clients on scheduling
   - Provide clear appointment details
   - Send reminders and confirmations

2. SCHEDULING COORDINATION:
   - Schedule depositions, mediations, and meetings
   - Coordinate with multiple parties
   - Find mutually convenient times

3. CALENDAR MANAGEMENT:
   - Track all scheduled appointments
   - Avoid scheduling conflicts
   - Manage rescheduling requests

4. PROCEEDING PREPARATION:
   - Ensure all parties are informed
   - Provide necessary preparation materials
   - Confirm attendance before proceedings

Remember: Proper scheduling prevents delays and keeps cases moving forward."""
    
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']
    
    def __init__(self):
        """Initialize the Voice Scheduler Agent"""
        logger.info('Initializing VoiceSchedulerAgent...')
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info('Gemini model initialized successfully.')
        except Exception as e:
            logger.error(f'Failed to initialize Gemini model: {e}', exc_info=True)
            raise
    
    async def ainvoke(self, query: str, case_context: str, session_id: str) -> Dict[str, Any]:
        """Process an appointment scheduling request"""
        logger.info(f"VoiceSchedulerAgent.ainvoke called with query: '{query}', session_id: '{session_id}'")
        
        try:
            prompt = f"""{self.SYSTEM_INSTRUCTION}

Case Context:
{case_context}

User Request: {query}

Extract appointment details and create a scheduling proposal.

Respond in JSON format:
{{
  "appointment_type": "Client Meeting|Deposition|Mediation|Court Hearing",
  "proposed_date": "YYYY-MM-DD",
  "proposed_time": "HH:MM",
  "duration": "X minutes",
  "attendees": ["person1", "person2"],
  "location": "location or virtual",
  "notes": "any additional notes",
  "summary": "brief summary"
}}
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.candidates[0].content.parts[0].text
            
            try:
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                parsed_response = json.loads(response_text)
            except:
                parsed_response = {'summary': response_text}
            
            content = f"""**Appointment Scheduling Proposal**

**Type:** {parsed_response.get('appointment_type', 'Meeting')}
**Date:** {parsed_response.get('proposed_date', 'TBD')}
**Time:** {parsed_response.get('proposed_time', 'TBD')}
**Duration:** {parsed_response.get('duration', 'TBD')}
**Location:** {parsed_response.get('location', 'TBD')}

**Attendees:**
{chr(10).join(['- ' + att for att in parsed_response.get('attendees', [])])}

**Notes:** {parsed_response.get('notes', '')}

**Summary:** {parsed_response.get('summary', '')}

---
*This appointment requires your approval before scheduling.*
"""
            
            logger.info(f'Successfully created scheduling proposal for session {session_id}')
            
            return {
                'is_task_complete': False,  # Needs approval
                'require_user_input': True,  # Requires approval
                'content': content,
                'metadata': {
                    **parsed_response,
                    'requires_approval': True,
                    'action_type': 'schedule_appointment'
                }
            }
        
        except Exception as e:
            logger.error(f'Error in VoiceSchedulerAgent.ainvoke: {e}', exc_info=True)
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'An error occurred: {str(e)}',
                'metadata': {'error': str(e)}
            }

