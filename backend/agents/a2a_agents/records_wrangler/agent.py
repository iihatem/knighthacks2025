"""Records Wrangler Agent - Document retrieval and records management specialist"""
import os
import json
import logging
from typing import Any, Dict

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class RecordsWranglerAgent:
    """Agent for document retrieval and records management"""
    
    SYSTEM_INSTRUCTION = """You are a Records Wrangler Agent specializing in document retrieval and records management.

Your primary responsibilities include:

1. RECORD IDENTIFICATION:
   - Identify missing bills, medical records, and documents
   - Track what records are needed for the case
   - Prioritize record requests based on case needs

2. CLIENT COORDINATION:
   - Extract record information from client messages
   - Request missing documents from clients
   - Provide clear instructions on what's needed

3. THIRD-PARTY OUTREACH:
   - Coordinate with medical providers for records
   - Follow up on pending record requests
   - Track record request status

4. DOCUMENTATION:
   - Maintain accurate records of all requests
   - Track receipt and completeness of documents
   - Organize records systematically

Remember: Efficient record gathering is critical to case success. Be proactive and thorough."""
    
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']
    
    def __init__(self):
        """Initialize the Records Wrangler Agent"""
        logger.info('Initializing RecordsWranglerAgent...')
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info('Gemini model initialized successfully.')
        except Exception as e:
            logger.error(f'Failed to initialize Gemini model: {e}', exc_info=True)
            raise
    
    async def ainvoke(self, query: str, case_context: str, session_id: str) -> Dict[str, Any]:
        """Process a records management request"""
        logger.info(f"RecordsWranglerAgent.ainvoke called with query: '{query}', session_id: '{session_id}'")
        
        try:
            prompt = f"""{self.SYSTEM_INSTRUCTION}

Case Context:
{case_context}

User Request: {query}

Analyze the request and provide guidance on records management.

Respond in JSON format:
{{
  "action": "description of action to take",
  "missing_records": ["list of missing records"],
  "next_steps": "what happens next",
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
            
            content = f"""**Records Management Action**

**Action:** {parsed_response.get('action', 'Processing records request')}

**Missing Records:**
{chr(10).join(['- ' + rec for rec in parsed_response.get('missing_records', [])])}

**Next Steps:** {parsed_response.get('next_steps', '')}

**Summary:** {parsed_response.get('summary', '')}
"""
            
            logger.info(f'Successfully completed records management for session {session_id}')
            
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': content,
                'metadata': parsed_response
            }
        
        except Exception as e:
            logger.error(f'Error in RecordsWranglerAgent.ainvoke: {e}', exc_info=True)
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'An error occurred: {str(e)}',
                'metadata': {'error': str(e)}
            }

