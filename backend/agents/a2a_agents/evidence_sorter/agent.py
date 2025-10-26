"""Evidence Sorter Agent - Document classification and organization specialist"""
import os
import json
import logging
from typing import Any, Dict

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class EvidenceSorterAgent:
    """Agent for document classification and evidence organization"""
    
    SYSTEM_INSTRUCTION = """You are an Evidence Sorter Agent specializing in document classification and organization.

Your primary responsibilities include:

1. EVIDENCE EXTRACTION:
   - Extract attachments from emails and messages
   - Identify relevant documents and media
   - Catalog all evidence systematically

2. ANALYSIS:
   - Analyze document content and relevance
   - Identify key evidence for the case
   - Flag important or sensitive materials

3. ORGANIZATION:
   - Label and categorize all evidence
   - Create logical folder structures
   - Maintain chain of custody

4. CASE MANAGEMENT INTEGRATION:
   - Upload evidence to case management system
   - Link evidence to relevant case events
   - Ensure evidence is easily retrievable

Remember: Proper evidence organization is crucial for case preparation and trial success."""
    
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']
    
    def __init__(self):
        """Initialize the Evidence Sorter Agent"""
        logger.info('Initializing EvidenceSorterAgent...')
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info('Gemini model initialized successfully.')
        except Exception as e:
            logger.error(f'Failed to initialize Gemini model: {e}', exc_info=True)
            raise
    
    async def ainvoke(self, query: str, case_context: str, session_id: str) -> Dict[str, Any]:
        """Process an evidence organization request"""
        logger.info(f"EvidenceSorterAgent.ainvoke called with query: '{query}', session_id: '{session_id}'")
        
        try:
            prompt = f"""{self.SYSTEM_INSTRUCTION}

Case Context:
{case_context}

User Request: {query}

Analyze the request and provide evidence organization guidance.

Respond in JSON format:
{{
  "action": "description of organization action",
  "categories": ["category1", "category2"],
  "priority_items": ["item1", "item2"],
  "organization_plan": "how to organize the evidence",
  "next_steps": "what to do next",
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
            
            content = f"""**Evidence Organization Plan**

**Action:** {parsed_response.get('action', 'Organizing evidence')}

**Categories:**
{chr(10).join(['- ' + cat for cat in parsed_response.get('categories', [])])}

**Priority Items:**
{chr(10).join(['- ' + item for item in parsed_response.get('priority_items', [])])}

**Organization Plan:**
{parsed_response.get('organization_plan', '')}

**Next Steps:** {parsed_response.get('next_steps', '')}

**Summary:** {parsed_response.get('summary', '')}
"""
            
            logger.info(f'Successfully created evidence organization plan for session {session_id}')
            
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': content,
                'metadata': parsed_response
            }
        
        except Exception as e:
            logger.error(f'Error in EvidenceSorterAgent.ainvoke: {e}', exc_info=True)
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'An error occurred: {str(e)}',
                'metadata': {'error': str(e)}
            }

