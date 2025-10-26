"""Script to create remaining A2A agent structures"""
import os

# Agent configurations
AGENTS = [
    {
        'name': 'records_wrangler',
        'class_name': 'RecordsWranglerAgent',
        'display_name': 'Records Wrangler Agent',
        'description': 'Pulls missing bills or records from client messages and coordinates with medical providers',
        'port': 10003,
        'instruction': """You are a Records Wrangler Agent specializing in document retrieval and records management.

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

Remember: Efficient record gathering is critical to case success. Be proactive and thorough.""",
        'skill_id': 'records_management',
        'skill_name': 'Records Management',
        'skill_description': 'Identify, request, and organize case records and documents',
        'examples': [
            'Pull medical records from the client\'s last message',
            'Request missing bills from the hospital',
            'Identify what documents we still need for this case'
        ]
    },
    {
        'name': 'voice_scheduler',
        'class_name': 'VoiceSchedulerAgent',
        'display_name': 'Voice Scheduler Agent',
        'description': 'Coordinates depositions, mediations, and client check-ins',
        'port': 10004,
        'instruction': """You are a Voice Scheduler Agent specializing in appointment coordination.

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

Remember: Proper scheduling prevents delays and keeps cases moving forward.""",
        'skill_id': 'appointment_scheduling',
        'skill_name': 'Appointment Scheduling',
        'skill_description': 'Schedule and coordinate legal proceedings and client meetings',
        'examples': [
            'Schedule a deposition for next week',
            'Arrange a mediation session with opposing counsel',
            'Set up a client check-in call'
        ]
    },
    {
        'name': 'evidence_sorter',
        'class_name': 'EvidenceSorterAgent',
        'display_name': 'Evidence Sorter Agent',
        'description': 'Extracts and labels attachments or media files from raw emails and organizes them',
        'port': 10005,
        'instruction': """You are an Evidence Sorter Agent specializing in document classification and organization.

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

Remember: Proper evidence organization is crucial for case preparation and trial success.""",
        'skill_id': 'evidence_organization',
        'skill_name': 'Evidence Organization',
        'skill_description': 'Extract, classify, and organize case evidence and documents',
        'examples': [
            'Sort and label the attachments from the client\'s email',
            'Organize all medical records by date',
            'Extract evidence from the latest correspondence'
        ]
    }
]

def create_agent_files(agent_config):
    """Create all files for an agent"""
    base_path = f"/Users/mac/Desktop/knighthacks2025/backend/agents/a2a_agents/{agent_config['name']}"
    os.makedirs(base_path, exist_ok=True)
    
    # __init__.py
    with open(f"{base_path}/__init__.py", 'w') as f:
        f.write(f'"""{agent_config["display_name"]} - A2A Server"""\n')
    
    # agent.py
    agent_code = f'''"""{agent_config["display_name"]} - {agent_config["description"]}"""
import os
import json
import logging
from typing import Any, Dict

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class {agent_config["class_name"]}:
    """Agent for {agent_config["description"].lower()}"""
    
    SYSTEM_INSTRUCTION = """{agent_config["instruction"]}"""
    
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']
    
    def __init__(self):
        """Initialize the {agent_config["display_name"]}"""
        logger.info('Initializing {agent_config["class_name"]}...')
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info('Gemini model initialized successfully.')
        except Exception as e:
            logger.error(f'Failed to initialize Gemini model: {{e}}', exc_info=True)
            raise
    
    async def ainvoke(self, query: str, case_context: str, session_id: str) -> Dict[str, Any]:
        """
        Process a task request
        
        Args:
            query: The user's request
            case_context: Context about the case from RAG
            session_id: Session ID for tracking
        
        Returns:
            Dict with task result
        """
        logger.info(f"{agent_config['class_name']}.ainvoke called with query: '{{query}}', session_id: '{{session_id}}'")
        
        try:
            prompt = f"""{{self.SYSTEM_INSTRUCTION}}

Case Context:
{{case_context}}

User Request: {{query}}

Provide a helpful response to the request. Be specific and actionable.

Respond in JSON format:
{{{{
  "action": "description of action to take",
  "details": "detailed information",
  "next_steps": "what happens next",
  "summary": "brief summary"
}}}}
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
                parsed_response = {{
                    'summary': response_text,
                    'details': response_text
                }}
            
            # Format the content for display
            content = f"""**{{parsed_response.get('action', 'Response')}}**

**Details:**
{{parsed_response.get('details', '')}}

**Next Steps:**
{{parsed_response.get('next_steps', '')}}

**Summary:** {{parsed_response.get('summary', '')}}
"""
            
            logger.info(f'Successfully completed task for session {{session_id}}')
            
            return {{
                'is_task_complete': True,
                'require_user_input': False,
                'content': content,
                'metadata': parsed_response
            }}
        
        except Exception as e:
            logger.error(f'Error in {agent_config["class_name"]}.ainvoke: {{e}}', exc_info=True)
            return {{
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'An error occurred: {{str(e)}}',
                'metadata': {{'error': str(e)}}
            }}
'''
    with open(f"{base_path}/agent.py", 'w') as f:
        f.write(agent_code)
    
    # executor.py
    executor_code = f'''"""{agent_config["display_name"]} Executor"""
import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from agents.shared.base_executor import BaseAgentExecutor
from agents.a2a_agents.{agent_config["name"]}.agent import {agent_config["class_name"]}


class {agent_config["class_name"]}Executor(BaseAgentExecutor):
    """Executor for {agent_config["display_name"]}"""
    
    def __init__(self):
        super().__init__('{agent_config["class_name"]}')
        self.agent = {agent_config["class_name"]}()
    
    async def process_task(self, query: str, case_id: str, session_id: str) -> Dict[str, Any]:
        case_context = f"Case ID: {{case_id}}"
        result = await self.agent.ainvoke(query, case_context, session_id)
        return result
'''
    with open(f"{base_path}/executor.py", 'w') as f:
        f.write(executor_code)
    
    # server.py
    server_code = f'''"""{agent_config["display_name"]} A2A Server"""
import os
import sys
import asyncio
import logging
import click
import uvicorn
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agents.a2a_agents.{agent_config["name"]}.executor import {agent_config["class_name"]}Executor
from agents.a2a_agents.{agent_config["name"]}.agent import {agent_config["class_name"]}

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = {agent_config["port"]}


def get_agent_card(host: str, port: int) -> AgentCard:
    capabilities = AgentCapabilities(streaming=True, push_notifications=False)
    skills = [
        AgentSkill(
            id='{agent_config["skill_id"]}',
            name='{agent_config["skill_name"]}',
            description='{agent_config["skill_description"]}',
            tags=['{agent_config["name"]}'],
            examples={agent_config["examples"]},
        ),
    ]
    app_url = os.environ.get('APP_URL', f'http://{{host}}:{{port}}')
    return AgentCard(
        name='{agent_config["display_name"]}',
        description='{agent_config["description"]}',
        url=app_url,
        version='1.0.0',
        default_input_modes={agent_config["class_name"]}.SUPPORTED_CONTENT_TYPES,
        default_output_modes={agent_config["class_name"]}.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=skills,
    )


def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, log_level: str = 'info'):
    if not os.getenv('GEMINI_API_KEY'):
        raise ValueError('GEMINI_API_KEY environment variable not set')
    
    async def run_server_async():
        logger.info('Initializing {agent_config["display_name"]} server...')
        executor = {agent_config["class_name"]}Executor()
        request_handler = DefaultRequestHandler(agent_executor=executor, task_store=InMemoryTaskStore())
        a2a_server = A2AStarletteApplication(agent_card=get_agent_card(host, port), http_handler=request_handler)
        asgi_app = a2a_server.build()
        config = uvicorn.Config(app=asgi_app, host=host, port=port, log_level=log_level.lower())
        uvicorn_server = uvicorn.Server(config)
        logger.info(f'Starting {agent_config["display_name"]} server at http://{{host}}:{{port}}')
        try:
            await uvicorn_server.serve()
        except KeyboardInterrupt:
            logger.info('Server shutdown requested.')
    
    try:
        asyncio.run(run_server_async())
    except Exception as e:
        logger.error(f'Error: {{e}}', exc_info=True)
        sys.exit(1)


@click.command()
@click.option('--host', default=DEFAULT_HOST)
@click.option('--port', default=DEFAULT_PORT, type=int)
@click.option('--log-level', default='info')
def cli(host: str, port: int, log_level: str):
    main(host, port, log_level)


if __name__ == '__main__':
    cli()
'''
    with open(f"{base_path}/server.py", 'w') as f:
        f.write(server_code)
    
    print(f"✓ Created {agent_config['display_name']} files")

# Create all agents
for agent in AGENTS:
    create_agent_files(agent)

print("\n✓ All remaining agents created successfully!")

