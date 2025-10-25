"""
A2A Server for TenderPilot Agents.
Implements A2A protocol for inter-agent communication.
"""
import asyncio
import logging
from typing import Dict, Any, List
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill
)
from agents import (
    TenderCoordinatorAgent,
    RecordsWranglerAgent,
    ClientCommunicationGuruAgent,
    LegalResearcherAgent,
    VoiceSchedulerAgent,
    EvidenceSorterAgent
)

logger = logging.getLogger(__name__)


class TenderPilotAgentExecutor(AgentExecutor):
    """
    A2A Agent Executor for TenderPilot agents.
    Handles A2A protocol requests and routes them to appropriate agents.
    """
    
    def __init__(self, coordinator: TenderCoordinatorAgent):
        """
        Initialize the A2A executor.
        
        Args:
            coordinator: TenderPilot coordinator agent
        """
        self.coordinator = coordinator
        self.logger = logging.getLogger(f"{__name__}.TenderPilotExecutor")
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Execute a task through the TenderPilot system.
        
        Args:
            context: A2A request context
            event_queue: Event queue for responses
        """
        self.logger.info(f"Processing A2A request: {context.message}")
        
        try:
            # Extract task information from A2A context
            task = self._extract_task_from_context(context)
            
            # Process through coordinator
            result = await self.coordinator.process(task)
            
            # Send response back via event queue
            await self._send_response(event_queue, result)
            
        except Exception as e:
            self.logger.error(f"Error processing A2A request: {str(e)}")
            await self._send_error(event_queue, str(e))
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Cancel a running task.
        
        Args:
            context: A2A request context
            event_queue: Event queue for responses
        """
        self.logger.info("Cancelling task (not implemented)")
        # For now, just acknowledge the cancellation
        await event_queue.enqueue_event(
            self._create_message("Task cancellation acknowledged")
        )
    
    def _extract_task_from_context(self, context: RequestContext) -> Dict[str, Any]:
        """
        Extract task information from A2A request context.
        
        Args:
            context: A2A request context
            
        Returns:
            Task dictionary
        """
        # Extract message content
        message_content = str(context.message) if context.message else ""
        
        # Parse task type from message or use default
        task_type = self._parse_task_type(message_content)
        
        # Extract metadata from context
        metadata = {
            "source": "a2a",
            "request_id": getattr(context, 'request_id', None),
            "timestamp": getattr(context, 'timestamp', None)
        }
        
        return {
            "task_type": task_type,
            "content": message_content,
            "metadata": metadata,
            "requires_approval": True  # Default to requiring approval
        }
    
    def _parse_task_type(self, message: str) -> str:
        """
        Parse task type from message content.
        
        Args:
            message: Message content
            
        Returns:
            Task type string
        """
        message_lower = message.lower()
        
        # Simple keyword-based parsing
        if any(word in message_lower for word in ["medical", "records", "billing"]):
            return "medical_records"
        elif any(word in message_lower for word in ["client", "message", "communication"]):
            return "client_communication"
        elif any(word in message_lower for word in ["research", "legal", "precedent"]):
            return "legal_research"
        elif any(word in message_lower for word in ["schedule", "appointment", "call"]):
            return "schedule_appointment"
        elif any(word in message_lower for word in ["document", "evidence", "organize"]):
            return "document_organization"
        else:
            return "general"
    
    async def _send_response(self, event_queue: EventQueue, result: Dict[str, Any]) -> None:
        """
        Send response back through event queue.
        
        Args:
            event_queue: Event queue
            result: Processing result
        """
        if result["status"] == "success":
            # Create success message
            message = self._format_success_message(result)
            await event_queue.enqueue_event(self._create_message(message))
        else:
            # Create error message
            error_msg = f"Error: {result.get('error', 'Unknown error')}"
            await event_queue.enqueue_event(self._create_message(error_msg))
    
    async def _send_error(self, event_queue: EventQueue, error: str) -> None:
        """
        Send error message through event queue.
        
        Args:
            event_queue: Event queue
            error: Error message
        """
        await event_queue.enqueue_event(
            self._create_message(f"System error: {error}")
        )
    
    def _create_message(self, content: str):
        """
        Create an A2A message.
        
        Args:
            content: Message content
            
        Returns:
            A2A message object
        """
        # This would use the actual A2A message creation
        # For now, we'll return a simple dict
        return {
            "type": "message",
            "content": content,
            "author": "TenderPilot"
        }
    
    def _format_success_message(self, result: Dict[str, Any]) -> str:
        """
        Format success result into readable message.
        
        Args:
            result: Processing result
            
        Returns:
            Formatted message string
        """
        agent = result.get("agent", "Unknown")
        confidence = result.get("confidence", "N/A")
        requires_approval = result.get("requires_approval", False)
        
        message = f"Task processed by {agent} (confidence: {confidence})"
        
        if requires_approval:
            message += "\n⚠️ This task requires human approval before execution."
        
        return message


class TenderPilotA2AServer:
    """
    A2A Server for TenderPilot system.
    Manages multiple agent services and their A2A endpoints.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Initialize the A2A server.
        
        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        
        # Initialize coordinator and agents
        self.coordinator = TenderCoordinatorAgent()
        self._register_agents()
        
        # Create agent cards and skills
        self.agent_cards = self._create_agent_cards()
        self.agent_skills = self._create_agent_skills()
    
    def _register_agents(self):
        """Register all specialized agents with coordinator."""
        agents = [
            RecordsWranglerAgent(),
            ClientCommunicationGuruAgent(),
            LegalResearcherAgent(),
            VoiceSchedulerAgent(),
            EvidenceSorterAgent()
        ]
        
        for agent in agents:
            self.coordinator.register_agent(agent)
            self.logger.info(f"Registered agent: {agent.name}")
    
    def _create_agent_skills(self) -> Dict[str, List[AgentSkill]]:
        """Create agent skills for each agent."""
        return {
            "RecordsWrangler": [
                AgentSkill(
                    id='medical_records_retrieval',
                    name='Medical Records Retrieval',
                    description='Requests and tracks medical records from providers',
                    tags=['medical', 'records', 'billing'],
                    examples=['Get MRI records from Dr. Smith', 'Request billing from hospital'],
                    input_modes=['text', 'application/json'],
                    output_modes=['text', 'application/json']
                )
            ],
            "ClientCommunicationGuru": [
                AgentSkill(
                    id='client_message_drafting',
                    name='Client Message Drafting',
                    description='Drafts empathetic and clear messages to clients',
                    tags=['communication', 'client', 'message'],
                    examples=['Draft case update for client', 'Send settlement notification'],
                    input_modes=['text'],
                    output_modes=['text']
                )
            ],
            "LegalResearcher": [
                AgentSkill(
                    id='legal_research',
                    name='Legal Research',
                    description='Finds case law, precedents, and legal citations',
                    tags=['research', 'legal', 'precedent'],
                    examples=['Find precedents for medical negligence', 'Research case law'],
                    input_modes=['text'],
                    output_modes=['text', 'application/json']
                )
            ],
            "VoiceScheduler": [
                AgentSkill(
                    id='appointment_scheduling',
                    name='Appointment Scheduling',
                    description='Schedules appointments via voice calls',
                    tags=['scheduling', 'voice', 'appointment'],
                    examples=['Schedule deposition', 'Book medical appointment'],
                    input_modes=['text'],
                    output_modes=['text']
                )
            ],
            "EvidenceSorter": [
                AgentSkill(
                    id='document_organization',
                    name='Document Organization',
                    description='Organizes and categorizes case documents',
                    tags=['documents', 'organization', 'evidence'],
                    examples=['Organize case files', 'Categorize evidence'],
                    input_modes=['text', 'application/json'],
                    output_modes=['text', 'application/json']
                )
            ]
        }
    
    def _create_agent_cards(self) -> Dict[str, AgentCard]:
        """Create agent cards for each agent."""
        base_url = f"http://{self.host}:{self.port}"
        
        cards = {}
        
        # Records Wrangler Agent Card
        cards["RecordsWrangler"] = AgentCard(
            name='Records Wrangler Agent',
            description='Handles medical records and billing requests from providers',
            url=f'{base_url}/records-wrangler',
            version='1.0.0',
            default_input_modes=['text'],
            default_output_modes=['text'],
            capabilities=AgentCapabilities(streaming=True),
            skills=self.agent_skills["RecordsWrangler"]
        )
        
        # Client Communication Guru Agent Card
        cards["ClientCommunicationGuru"] = AgentCard(
            name='Client Communication Guru',
            description='Drafts clear, empathetic messages to clients',
            url=f'{base_url}/client-communication',
            version='1.0.0',
            default_input_modes=['text'],
            default_output_modes=['text'],
            capabilities=AgentCapabilities(streaming=True),
            skills=self.agent_skills["ClientCommunicationGuru"]
        )
        
        # Legal Researcher Agent Card
        cards["LegalResearcher"] = AgentCard(
            name='Legal Researcher Agent',
            description='Finds case law, precedents, and legal citations',
            url=f'{base_url}/legal-researcher',
            version='1.0.0',
            default_input_modes=['text'],
            default_output_modes=['text'],
            capabilities=AgentCapabilities(streaming=True),
            skills=self.agent_skills["LegalResearcher"]
        )
        
        # Voice Scheduler Agent Card
        cards["VoiceScheduler"] = AgentCard(
            name='Voice Scheduler Agent',
            description='Coordinates appointments via voice calls',
            url=f'{base_url}/voice-scheduler',
            version='1.0.0',
            default_input_modes=['text'],
            default_output_modes=['text'],
            capabilities=AgentCapabilities(streaming=True),
            skills=self.agent_skills["VoiceScheduler"]
        )
        
        # Evidence Sorter Agent Card
        cards["EvidenceSorter"] = AgentCard(
            name='Evidence Sorter Agent',
            description='Organizes documents, evidence, and attachments',
            url=f'{base_url}/evidence-sorter',
            version='1.0.0',
            default_input_modes=['text'],
            default_output_modes=['text'],
            capabilities=AgentCapabilities(streaming=True),
            skills=self.agent_skills["EvidenceSorter"]
        )
        
        return cards
    
    def create_main_agent_card(self) -> AgentCard:
        """Create the main TenderPilot agent card."""
        base_url = f"http://{self.host}:{self.port}"
        
        # Main coordinator skill
        coordinator_skill = AgentSkill(
            id='legal_task_orchestration',
            name='Legal Task Orchestration',
            description='Orchestrates legal tasks and routes them to specialized agents',
            tags=['legal', 'orchestration', 'routing'],
            examples=['Process legal task', 'Route medical records request'],
            input_modes=['text'],
            output_modes=['text']
        )
        
        return AgentCard(
            name='TenderPilot Legal Orchestrator',
            description='AI-powered legal tender orchestrator for Morgan & Morgan',
            url=f'{base_url}/',
            version='1.0.0',
            default_input_modes=['text'],
            default_output_modes=['text'],
            capabilities=AgentCapabilities(streaming=True),
            skills=[coordinator_skill],
            supports_authenticated_extended_card=True
        )
    
    async def start_server(self):
        """Start the A2A server."""
        self.logger.info("Starting TenderPilot A2A Server...")
        
        # Create main agent executor
        main_executor = TenderPilotAgentExecutor(self.coordinator)
        
        # Create request handler
        request_handler = DefaultRequestHandler(
            agent_executor=main_executor,
            task_store=InMemoryTaskStore()
        )
        
        # Create main agent card
        main_agent_card = self.create_main_agent_card()
        
        # Create A2A application
        a2a_app = A2AStarletteApplication(
            agent_card=main_agent_card,
            http_handler=request_handler
        )
        
        # Start server
        import uvicorn
        self.logger.info(f"Starting server on {self.host}:{self.port}")
        
        config = uvicorn.Config(
            a2a_app.build(),
            host=self.host,
            port=self.port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    def get_agent_cards(self) -> Dict[str, AgentCard]:
        """Get all agent cards."""
        return self.agent_cards
    
    def get_agent_skills(self) -> Dict[str, List[AgentSkill]]:
        """Get all agent skills."""
        return self.agent_skills


async def main():
    """Main entry point for A2A server."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    server = TenderPilotA2AServer(host="0.0.0.0", port=8000)
    await server.start_server()


if __name__ == "__main__":
    asyncio.run(main())
