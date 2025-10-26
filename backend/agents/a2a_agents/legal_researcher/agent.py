"""Legal Researcher Agent - Case law and precedent research specialist"""
import os
import json
import logging
from typing import Any, Dict

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class LegalResearcherAgent:
    """Agent for legal research and case law analysis"""
    
    SYSTEM_INSTRUCTION = """You are a Legal Researcher Agent specializing in case law and precedent research.

Your primary responsibilities include:

1. PRECEDENT RESEARCH:
   - Find relevant case law and legal precedents
   - Identify supporting verdicts and citations
   - Analyze how precedents apply to current cases
   - Track recent legal developments

2. CASE STRENGTHENING:
   - Identify legal arguments that strengthen the case
   - Find weaknesses in opposing arguments
   - Suggest novel legal theories to explore
   - Provide strategic research insights

3. LEGAL ANALYSIS:
   - Analyze complex legal issues
   - Provide clear summaries of relevant law
   - Explain how statutes and regulations apply
   - Identify potential legal risks and opportunities

4. STRATEGIC RESEARCH:
   - Prioritize research based on case needs
   - Focus on high-impact legal issues
   - Provide actionable research recommendations
   - Stay current with legal developments

Remember: Your research should be thorough, accurate, and directly applicable to the case at hand.
"""
    
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']
    
    def __init__(self):
        """Initialize the Legal Researcher Agent"""
        logger.info('Initializing LegalResearcherAgent...')
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info('Gemini model initialized successfully.')
        except Exception as e:
            logger.error(f'Failed to initialize Gemini model: {e}', exc_info=True)
            raise
    
    async def ainvoke(self, query: str, case_context: str, session_id: str) -> Dict[str, Any]:
        """
        Process a legal research request
        
        Args:
            query: The user's research request
            case_context: Context about the case from RAG
            session_id: Session ID for tracking
        
        Returns:
            Dict with task result
        """
        logger.info(f"LegalResearcherAgent.ainvoke called with query: '{query}', session_id: '{session_id}'")
        
        try:
            prompt = f"""{self.SYSTEM_INSTRUCTION}

Case Context:
{case_context}

Research Request: {query}

Provide comprehensive legal research guidance including:
1. Key search terms and databases to check
2. Relevant legal precedents or statutes to review
3. Potential legal arguments or theories
4. Strategic recommendations

Respond in JSON format:
{{
  "search_terms": ["term1", "term2"],
  "databases": ["database1", "database2"],
  "precedents": ["precedent1", "precedent2"],
  "legal_theories": ["theory1", "theory2"],
  "recommendations": "strategic recommendations",
  "summary": "brief summary of research guidance"
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
                parsed_response = {
                    'summary': response_text,
                    'recommendations': response_text
                }
            
            # Format the content for display
            content = f"""**Legal Research Guidance**

**Summary:** {parsed_response.get('summary', 'Research guidance provided')}

**Key Search Terms:**
{chr(10).join(['- ' + term for term in parsed_response.get('search_terms', [])])}

**Databases to Check:**
{chr(10).join(['- ' + db for db in parsed_response.get('databases', [])])}

**Relevant Precedents:**
{chr(10).join(['- ' + prec for prec in parsed_response.get('precedents', [])])}

**Legal Theories to Explore:**
{chr(10).join(['- ' + theory for theory in parsed_response.get('legal_theories', [])])}

**Strategic Recommendations:**
{parsed_response.get('recommendations', '')}
"""
            
            logger.info(f'Successfully completed legal research for session {session_id}')
            
            return {
                'is_task_complete': True,  # Research guidance doesn't need approval
                'require_user_input': False,
                'content': content,
                'metadata': parsed_response
            }
        
        except Exception as e:
            logger.error(f'Error in LegalResearcherAgent.ainvoke: {e}', exc_info=True)
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'An error occurred during legal research: {str(e)}',
                'metadata': {'error': str(e)}
            }

