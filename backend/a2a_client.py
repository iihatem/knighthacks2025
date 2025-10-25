"""
A2A Client for TenderPilot Agents.
Enables inter-agent communication using A2A protocol.
"""
import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class A2AAgent:
    """Represents an A2A agent."""
    name: str
    url: str
    skills: List[Dict[str, Any]]
    capabilities: Dict[str, Any]


class TenderPilotA2AClient:
    """
    A2A Client for TenderPilot system.
    Manages communication with A2A agents.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the A2A client.
        
        Args:
            base_url: Base URL for A2A server
        """
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.agents: Dict[str, A2AAgent] = {}
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        await self.discover_agents()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def discover_agents(self):
        """Discover available A2A agents."""
        self.logger.info("Discovering A2A agents...")
        
        # List of known agent endpoints
        agent_endpoints = [
            "/records-wrangler",
            "/client-communication", 
            "/legal-researcher",
            "/voice-scheduler",
            "/evidence-sorter"
        ]
        
        for endpoint in agent_endpoints:
            try:
                agent_url = f"{self.base_url}{endpoint}"
                agent_card = await self._get_agent_card(agent_url)
                
                if agent_card:
                    agent = A2AAgent(
                        name=agent_card.get("name", endpoint),
                        url=agent_url,
                        skills=agent_card.get("skills", []),
                        capabilities=agent_card.get("capabilities", {})
                    )
                    self.agents[agent.name] = agent
                    self.logger.info(f"Discovered agent: {agent.name}")
                    
            except Exception as e:
                self.logger.warning(f"Failed to discover agent at {endpoint}: {str(e)}")
    
    async def _get_agent_card(self, agent_url: str) -> Optional[Dict[str, Any]]:
        """
        Get agent card from agent URL.
        
        Args:
            agent_url: Agent URL
            
        Returns:
            Agent card dictionary or None
        """
        try:
            card_url = f"{agent_url}/.well-known/agent-card.json"
            async with self.session.get(card_url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.warning(f"Failed to get agent card: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Error getting agent card: {str(e)}")
            return None
    
    async def send_message(self, agent_name: str, message: str, **kwargs) -> Dict[str, Any]:
        """
        Send a message to a specific agent.
        
        Args:
            agent_name: Name of the target agent
            message: Message content
            **kwargs: Additional parameters
            
        Returns:
            Response from agent
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")
        
        agent = self.agents[agent_name]
        
        # Prepare message payload
        payload = {
            "message": message,
            "input_mode": "text",
            "output_mode": "text",
            **kwargs
        }
        
        try:
            # Send message via A2A protocol
            message_url = f"{agent.url}/message/send"
            
            async with self.session.post(
                message_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Message sent to {agent_name}: {result}")
                    return result
                else:
                    error_msg = f"Failed to send message: {response.status}"
                    self.logger.error(error_msg)
                    return {"error": error_msg}
                    
        except Exception as e:
            error_msg = f"Error sending message to {agent_name}: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}
    
    async def stream_message(self, agent_name: str, message: str, **kwargs):
        """
        Stream a message to a specific agent.
        
        Args:
            agent_name: Name of the target agent
            message: Message content
            **kwargs: Additional parameters
            
        Yields:
            Streamed responses from agent
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")
        
        agent = self.agents[agent_name]
        
        # Prepare message payload
        payload = {
            "message": message,
            "input_mode": "text",
            "output_mode": "text",
            **kwargs
        }
        
        try:
            # Stream message via A2A protocol
            stream_url = f"{agent.url}/message/stream"
            
            async with self.session.post(
                stream_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    async for line in response.content:
                        if line:
                            try:
                                # Parse JSON line
                                data = await response.json()
                                yield data
                            except:
                                # If not JSON, yield as text
                                yield {"content": line.decode()}
                else:
                    yield {"error": f"Stream failed: {response.status}"}
                    
        except Exception as e:
            yield {"error": f"Stream error: {str(e)}"}
    
    async def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent information or None
        """
        if agent_name not in self.agents:
            return None
        
        agent = self.agents[agent_name]
        return {
            "name": agent.name,
            "url": agent.url,
            "skills": agent.skills,
            "capabilities": agent.capabilities
        }
    
    def list_agents(self) -> List[str]:
        """
        List available agents.
        
        Returns:
            List of agent names
        """
        return list(self.agents.keys())
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all agents.
        
        Returns:
            Dictionary of agent health status
        """
        health_status = {}
        
        for agent_name, agent in self.agents.items():
            try:
                # Try to get agent card as health check
                card_url = f"{agent.url}/.well-known/agent-card.json"
                async with self.session.get(card_url, timeout=5) as response:
                    health_status[agent_name] = response.status == 200
            except:
                health_status[agent_name] = False
        
        return health_status


class TenderPilotOrchestrator:
    """
    Orchestrator that uses A2A client to coordinate between agents.
    """
    
    def __init__(self, a2a_client: TenderPilotA2AClient):
        """
        Initialize the orchestrator.
        
        Args:
            a2a_client: A2A client instance
        """
        self.client = a2a_client
        self.logger = logging.getLogger(__name__)
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task by routing it to the appropriate agent.
        
        Args:
            task: Task dictionary
            
        Returns:
            Processing result
        """
        task_type = task.get("task_type", "general")
        content = task.get("content", "")
        
        # Determine target agent based on task type
        target_agent = self._determine_target_agent(task_type)
        
        if not target_agent:
            return {
                "status": "error",
                "error": f"No suitable agent found for task type: {task_type}"
            }
        
        self.logger.info(f"Routing task to {target_agent}")
        
        try:
            # Send message to target agent
            result = await self.client.send_message(
                agent_name=target_agent,
                message=content,
                task_type=task_type,
                metadata=task.get("metadata", {})
            )
            
            return {
                "status": "success",
                "agent": target_agent,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent": target_agent
            }
    
    def _determine_target_agent(self, task_type: str) -> Optional[str]:
        """
        Determine which agent should handle the task.
        
        Args:
            task_type: Type of task
            
        Returns:
            Agent name or None
        """
        # Mapping of task types to agent names
        task_agent_mapping = {
            "medical_records": "Records Wrangler Agent",
            "billing_request": "Records Wrangler Agent",
            "client_communication": "Client Communication Guru",
            "client_message": "Client Communication Guru",
            "legal_research": "Legal Researcher Agent",
            "case_law": "Legal Researcher Agent",
            "schedule_appointment": "Voice Scheduler Agent",
            "schedule_deposition": "Voice Scheduler Agent",
            "document_organization": "Evidence Sorter Agent",
            "evidence_upload": "Evidence Sorter Agent"
        }
        
        return task_agent_mapping.get(task_type)


async def test_a2a_client():
    """Test the A2A client functionality."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Testing A2A Client...")
    
    async with TenderPilotA2AClient() as client:
        # List discovered agents
        agents = client.list_agents()
        logger.info(f"Discovered agents: {agents}")
        
        # Check health
        health = await client.health_check()
        logger.info(f"Agent health: {health}")
        
        # Test message sending (if agents are available)
        if agents:
            test_message = "Test message for agent communication"
            try:
                result = await client.send_message(
                    agent_name=agents[0],
                    message=test_message
                )
                logger.info(f"Message result: {result}")
            except Exception as e:
                logger.error(f"Error sending message: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_a2a_client())
