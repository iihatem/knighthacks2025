"""Host Orchestrator Agent - Routes tasks to specialist A2A agents"""
import os
import sys
import uuid
import json
import logging
import asyncio
from typing import Any, Dict, List

import httpx
import google.generativeai as genai
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RemoteAgentConnection:
    """Manages connection to a remote A2A agent"""
    
    def __init__(self, agent_card: AgentCard, agent_url: str):
        self.agent_card = agent_card
        self.agent_url = agent_url
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def send_message(self, message_request: SendMessageRequest) -> SendMessageResponse:
        """Send a message to the remote agent using JSON-RPC"""
        try:
            # A2A uses JSON-RPC 2.0, so we send to the root endpoint
            # The method is specified in the JSON-RPC payload
            json_rpc_request = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": message_request.params.model_dump(exclude_none=True),
                "id": message_request.id
            }
            
            response = await self.client.post(
                self.agent_url,  # Root URL, not /message/send
                json=json_rpc_request,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            # Parse JSON-RPC response
            json_response = response.json()
            
            # Check for JSON-RPC error
            if "error" in json_response:
                error = json_response["error"]
                raise Exception(f"JSON-RPC Error {error.get('code')}: {error.get('message')}")
            
            # Extract result and wrap in SendMessageResponse
            if "result" in json_response:
                return SendMessageResponse.model_validate({
                    "jsonrpc": "2.0",
                    "result": json_response["result"],
                    "id": json_response.get("id")
                })
            else:
                raise Exception("Invalid JSON-RPC response: missing 'result' field")
                
        except Exception as e:
            logger.error(f"Error sending message to {self.agent_card.name}: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class HostOrchestrator:
    """Main orchestrator that routes tasks to specialist A2A agents"""
    
    def __init__(self):
        self.remote_agents: Dict[str, RemoteAgentConnection] = {}
        self.agent_cards: Dict[str, AgentCard] = {}
        self.model = None
        logger.info("Initializing HostOrchestrator...")
    
    async def init_agents(self, agent_urls: List[str]):
        """
        Discover and connect to remote A2A agents
        
        Args:
            agent_urls: List of agent URLs to connect to
        """
        logger.info(f"Discovering {len(agent_urls)} remote agents...")
        
        async with httpx.AsyncClient(timeout=30) as client:
            for url in agent_urls:
                try:
                    # Fetch Agent Card
                    card_resolver = A2ACardResolver(client, url)
                    card = await card_resolver.get_agent_card()
                    
                    # Create connection
                    connection = RemoteAgentConnection(card, url)
                    self.remote_agents[card.name] = connection
                    self.agent_cards[card.name] = card
                    
                    logger.info(f"✓ Connected to {card.name} at {url}")
                    logger.info(f"  Skills: {[skill.name for skill in (card.skills or [])]}")
                
                except Exception as e:
                    logger.error(f"✗ Failed to connect to agent at {url}: {e}")
        
        # Initialize Gemini model
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("✓ Gemini model initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise
        
        logger.info(f"HostOrchestrator initialized with {len(self.remote_agents)} agents")
    
    def get_agents_description(self) -> str:
        """Get a formatted description of all available agents"""
        descriptions = []
        for name, card in self.agent_cards.items():
            skills = [skill.name for skill in (card.skills or [])]
            descriptions.append(f"- **{name}**: {card.description} (Skills: {', '.join(skills)})")
        return "\n".join(descriptions)
    
    async def analyze_intent(self, query: str, case_context: str, recent_messages: List[Dict]) -> Dict[str, Any]:
        """
        Analyze user query to determine which agent(s) to use
        
        Args:
            query: User's query
            case_context: Context about the case
            recent_messages: Recent conversation history
        
        Returns:
            Dict with analysis results
        """
        context_text = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in recent_messages])
        
        prompt = f"""You are an AI orchestrator analyzing a legal query to determine which specialist agent(s) to use.

Available Agents:
{self.get_agents_description()}

Recent Conversation:
{context_text if context_text else "No previous conversation"}

Case Context:
{case_context}

User Query: "{query}"

Analyze the query and determine:
1. Which agent is best suited for this task?
2. What is the main intent/action type?
3. Is this a continuation of the previous conversation?

Action types:
- draft_email: Draft email to client/opposing counsel → Client Communication Agent
- draft_message: Draft message for client → Client Communication Agent
- schedule_appointment: Schedule deposition/mediation → Voice Scheduler Agent
- research_legal: Research case law, precedents → Legal Researcher Agent
- manage_records: Request/organize documents → Records Wrangler Agent
- organize_evidence: Classify/organize evidence → Evidence Sorter Agent
- general_query: General question/analysis → Handle directly

Respond in JSON format:
{{
  "agent_name": "exact agent name from the list above or 'Orchestrator' for general queries",
  "action_type": "one of the action types above",
  "is_continuation": true or false,
  "reasoning": "brief explanation of your decision",
  "requires_approval": true or false
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.candidates[0].content.parts[0].text
            
            # Parse JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(response_text)
            logger.info(f"Intent analysis: {analysis.get('agent_name')} - {analysis.get('action_type')}")
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            # Fallback
            return {
                "agent_name": "Orchestrator",
                "action_type": "general_query",
                "is_continuation": False,
                "reasoning": f"Failed to analyze intent: {e}",
                "requires_approval": False
            }
    
    async def delegate_to_agent(self, agent_name: str, query: str, case_id: str, session_id: str) -> Dict[str, Any]:
        """
        Delegate a task to a remote A2A agent
        
        Args:
            agent_name: Name of the agent to delegate to
            query: The task/query to send
            case_id: Case ID
            session_id: Session ID
        
        Returns:
            Dict with agent response
        """
        if agent_name not in self.remote_agents:
            raise ValueError(f"Agent '{agent_name}' not found. Available: {list(self.remote_agents.keys())}")
        
        connection = self.remote_agents[agent_name]
        
        # Create A2A message
        message_id = str(uuid.uuid4())
        message_request = SendMessageRequest(
            id=message_id,
            params=MessageSendParams(
                message={
                    'role': 'user',
                    'parts': [{'type': 'text', 'text': query}],
                    'messageId': message_id,
                    'metadata': {'case_id': case_id}
                }
            )
        )
        
        logger.info(f"Delegating to {agent_name}: {query[:100]}...")
        
        try:
            # Send message to remote agent
            response = await connection.send_message(message_request)
            
            # Debug: Log the response structure
            logger.debug(f"Received response from {agent_name}: {response}")
            
            # Extract result
            if isinstance(response.root, SendMessageSuccessResponse):
                if isinstance(response.root.result, Task):
                    task = response.root.result
                    
                    # Debug logging
                    logger.info(f"Task received - Status: {task.status.state if task.status else 'None'}")
                    if task.status and task.status.message:
                        logger.debug(f"Task status message: {task.status.message}")
                    if task.artifacts:
                        logger.debug(f"Task artifacts count: {len(task.artifacts)}")
                    
                    # Extract content from task artifacts or status
                    content = "Task submitted successfully"
                    metadata = {}
                    requires_approval = False
                    
                    # Check task status for messages (priority: status message first)
                    if task.status and task.status.message:
                        status_msg = task.status.message
                        logger.debug(f"Status message type: {type(status_msg)}")
                        
                        # The message might be a Message object with parts
                        if hasattr(status_msg, 'parts') and status_msg.parts:
                            for part in status_msg.parts:
                                logger.debug(f"Status message part: {part}")
                                # Part might be a dict or a Part object
                                if isinstance(part, dict):
                                    if part.get('type') == 'text':
                                        content = part.get('text', content)
                                    elif part.get('type') == 'data':
                                        metadata.update(part.get('data', {}))
                                elif hasattr(part, 'type'):
                                    if part.type == 'text' and hasattr(part, 'text'):
                                        content = part.text
                                    elif part.type == 'data' and hasattr(part, 'data'):
                                        metadata.update(part.data)
                    
                    # Also check artifacts (might contain the final result)
                    if task.artifacts:
                        for artifact in task.artifacts:
                            logger.debug(f"Artifact: {artifact}")
                            if hasattr(artifact, 'parts') and artifact.parts:
                                for part in artifact.parts:
                                    logger.debug(f"Artifact part: {part}")
                                    if isinstance(part, dict):
                                        if part.get('type') == 'text':
                                            # Don't overwrite if we already have content from status
                                            if content == "Task submitted successfully":
                                                content = part.get('text', content)
                                        elif part.get('type') == 'data':
                                            metadata.update(part.get('data', {}))
                                    elif hasattr(part, 'type'):
                                        if part.type == 'text' and hasattr(part, 'text'):
                                            if content == "Task submitted successfully":
                                                content = part.text
                                        elif part.type == 'data' and hasattr(part, 'data'):
                                            metadata.update(part.data)
                    
                    # Check if approval is required from metadata or task status
                    if metadata.get('requires_approval'):
                        requires_approval = True
                    if task.status and hasattr(task.status, 'state'):
                        if task.status.state == 'input_required':
                            requires_approval = True
                    
                    logger.info(f"Extracted content length: {len(content)}, requires_approval: {requires_approval}")
                    
                    return {
                        'success': True,
                        'agent': agent_name,
                        'content': content,
                        'metadata': metadata,
                        'task_id': task.id,
                        'status': task.status.state if task.status else 'unknown',
                        'requires_approval': requires_approval
                    }
                else:
                    # Direct message response
                    return {
                        'success': True,
                        'agent': agent_name,
                        'content': str(response.root.result),
                        'metadata': {}
                    }
            else:
                return {
                    'success': False,
                    'agent': agent_name,
                    'content': f"Unexpected response type from {agent_name}",
                    'metadata': {}
                }
        
        except Exception as e:
            logger.error(f"Error delegating to {agent_name}: {e}", exc_info=True)
            return {
                'success': False,
                'agent': agent_name,
                'content': f"Error communicating with {agent_name}: {str(e)}",
                'metadata': {'error': str(e)}
            }
    
    async def handle_general_query(self, query: str, case_context: str) -> Dict[str, Any]:
        """Handle general queries that don't need a specialist agent"""
        try:
            prompt = f"""You are a helpful legal AI assistant.

Case Context:
{case_context}

User Question: {query}

Provide a helpful, professional response."""
            
            response = self.model.generate_content(prompt)
            content = response.candidates[0].content.parts[0].text
            
            return {
                'success': True,
                'agent': 'Orchestrator',
                'content': content,
                'metadata': {}
            }
        
        except Exception as e:
            logger.error(f"Error handling general query: {e}")
            return {
                'success': False,
                'agent': 'Orchestrator',
                'content': f"Error: {str(e)}",
                'metadata': {'error': str(e)}
            }
    
    async def process(
        self,
        case_id: str,
        query: str,
        case_context: str = "",
        session_id: str = None,
        recent_messages: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main processing function - analyzes intent and routes to appropriate agent
        
        Args:
            case_id: Case ID
            query: User's query
            case_context: Context about the case
            session_id: Optional session ID
            recent_messages: Recent conversation history
        
        Returns:
            Dict with processing result
        """
        if recent_messages is None:
            recent_messages = []
        
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Analyze intent
        analysis = await self.analyze_intent(query, case_context, recent_messages)
        
        agent_name = analysis.get('agent_name', 'Orchestrator')
        action_type = analysis.get('action_type', 'general_query')
        
        # Route to appropriate agent
        if agent_name == 'Orchestrator' or action_type == 'general_query':
            result = await self.handle_general_query(query, case_context)
        else:
            result = await self.delegate_to_agent(agent_name, query, case_id, session_id)
        
        # Build response
        return {
            'status': 'success' if result.get('success', False) else 'error',
            'session_id': session_id,
            'agent_type': agent_name,
            'action_type': action_type,
            'requires_approval': analysis.get('requires_approval', False),
            'result': result.get('content', ''),
            'metadata': result.get('metadata', {}),
            'reasoning': analysis.get('reasoning', ''),
            'is_continuation': analysis.get('is_continuation', False)
        }
    
    async def close(self):
        """Close all connections"""
        for connection in self.remote_agents.values():
            await connection.close()
        logger.info("HostOrchestrator connections closed")
    
    @classmethod
    async def create(cls, agent_urls: List[str] = None) -> 'HostOrchestrator':
        """
        Factory method to create and initialize a HostOrchestrator
        
        Args:
            agent_urls: List of agent URLs (defaults to localhost:10001-10005)
        
        Returns:
            Initialized HostOrchestrator instance
        """
        if agent_urls is None:
            agent_urls = [
                'http://localhost:10001',  # Client Communication
                'http://localhost:10002',  # Legal Researcher
                'http://localhost:10003',  # Records Wrangler
                'http://localhost:10004',  # Voice Scheduler
                'http://localhost:10005',  # Evidence Sorter
            ]
        
        orchestrator = cls()
        await orchestrator.init_agents(agent_urls)
        return orchestrator


# Global instance (will be initialized by app.py)
_orchestrator_instance: HostOrchestrator = None


async def get_orchestrator() -> HostOrchestrator:
    """Get or create the global orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = await HostOrchestrator.create()
    return _orchestrator_instance


async def shutdown_orchestrator():
    """Shutdown the global orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is not None:
        await _orchestrator_instance.close()
        _orchestrator_instance = None

