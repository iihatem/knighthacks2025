"""Client Communication Agent - Empathetic message drafting specialist"""
import os
import json
import logging
from typing import Any, Dict

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ClientCommunicationAgent:
    """Agent for drafting empathetic client communications"""
    
    SYSTEM_INSTRUCTION = """You are the Client Communication Guru for a law firm.

Your primary responsibilities include:

1. MESSAGE DRAFTING:
   - Draft professional, clear, and empathetic communications to clients
   - Ensure all messages maintain a professional yet warm tone
   - Use plain English (no legal jargon unless necessary)
   - Structure messages with clear headings and bullet points when appropriate

2. QUALITY CONTROL:
   - Review all outgoing communications for accuracy and completeness
   - Ensure messages are free of grammatical errors and typos
   - Verify that all necessary information is included
   - Check that sensitive information is handled appropriately

3. CLIENT RELATIONSHIP MANAGEMENT:
   - Maintain a professional and empathetic tone in all communications
   - Address client concerns and questions promptly
   - Ensure messages reflect the firm's values and commitment to client service
   - Adapt communication style to match the urgency and nature of the message

4. COMPLIANCE AND CONFIDENTIALITY:
   - Ensure all communications comply with legal and ethical standards
   - Protect client confidentiality in all messages
   - Include appropriate disclaimers when necessary

Remember: You are the face of the firm to clients. Every message you draft should reflect professionalism, empathy, and legal expertise.
"""
    
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']
    
    def __init__(self):
        """Initialize the Client Communication Agent"""
        logger.info('Initializing ClientCommunicationAgent...')
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info('Gemini model initialized successfully.')
        except Exception as e:
            logger.error(f'Failed to initialize Gemini model: {e}', exc_info=True)
            raise
    
    async def ainvoke(self, query: str, case_context: str, session_id: str) -> Dict[str, Any]:
        """
        Process a client communication request
        
        Args:
            query: The user's request (e.g., "draft an email to client about deposition")
            case_context: Context about the case from RAG
            session_id: Session ID for tracking
        
        Returns:
            Dict with:
                - is_task_complete: bool
                - require_user_input: bool (True for approval)
                - content: str (the drafted message)
                - metadata: dict (additional info like to, subject, etc.)
        """
        logger.info(f"ClientCommunicationAgent.ainvoke called with query: '{query}', session_id: '{session_id}'")
        
        try:
            prompt = f"""{self.SYSTEM_INSTRUCTION}

Case Context:
{case_context}

User Request: {query}

Draft a professional, empathetic communication. If it's an email, provide the subject line and body.
If it's a general message, just provide the message text.

Respond in JSON format:
{{
  "type": "email" or "message",
  "to": "recipient (if email)",
  "subject": "subject line (if email)",
  "body": "the full message text",
  "notes": "any additional notes or considerations"
}}
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.candidates[0].content.parts[0].text
            
            # Try to parse JSON response
            try:
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                parsed_response = json.loads(response_text)
            except:
                # Fallback if JSON parsing fails
                parsed_response = {
                    'type': 'message',
                    'body': response_text,
                    'notes': 'Response could not be parsed as JSON'
                }
            
            # Format the content for display
            if parsed_response.get('type') == 'email':
                content = f"""**Email Draft**

**To:** {parsed_response.get('to', 'Client')}
**Subject:** {parsed_response.get('subject', 'Case Update')}

**Message:**
{parsed_response.get('body', '')}

---
*This draft requires your approval before sending.*
"""
            else:
                content = f"""**Message Draft**

{parsed_response.get('body', '')}

---
*This draft requires your approval before sending.*
"""
            
            logger.info(f'Successfully drafted communication for session {session_id}')
            
            return {
                'is_task_complete': False,  # Needs approval
                'require_user_input': True,  # Requires approval
                'content': content,
                'metadata': {
                    'type': parsed_response.get('type'),
                    'to': parsed_response.get('to'),
                    'subject': parsed_response.get('subject'),
                    'body': parsed_response.get('body'),
                    'notes': parsed_response.get('notes'),
                    'requires_approval': True,
                    'action_type': 'draft_email'
                }
            }
        
        except Exception as e:
            logger.error(f'Error in ClientCommunicationAgent.ainvoke: {e}', exc_info=True)
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'An error occurred while drafting the communication: {str(e)}',
                'metadata': {'error': str(e)}
            }

