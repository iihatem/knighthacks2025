"""
TenderPilot Coordinator Agent.
Main orchestrator that routes tasks to specialized agents.
"""
from typing import Dict, Any, List, Optional
import logging
from .base_agent import TenderPilotBaseAgent

logger = logging.getLogger(__name__)


class TenderCoordinatorAgent(TenderPilotBaseAgent):
    """
    Main coordinator agent that routes legal tasks to appropriate specialists.
    Implements the Coordinator/Dispatcher pattern from Google ADK.
    """
    
    def __init__(self):
        """Initialize the coordinator agent."""
        super().__init__(
            name="TenderCoordinator",
            description="Main legal tender orchestrator that routes tasks to specialized agents"
        )
        self.sub_agents: Dict[str, TenderPilotBaseAgent] = {}
        self.task_routing_rules = self._initialize_routing_rules()
    
    def register_agent(self, agent: TenderPilotBaseAgent):
        """
        Register a specialized agent with the coordinator.
        
        Args:
            agent: Specialized agent to register
        """
        self.sub_agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    def _initialize_routing_rules(self) -> Dict[str, List[str]]:
        """
        Initialize task routing rules.
        Maps task types to agent names.
        
        Returns:
            Dictionary of task types to agent names
        """
        return {
            "medical_records": ["RecordsWrangler"],
            "billing_request": ["RecordsWrangler"],
            "client_communication": ["ClientCommunicationGuru"],
            "client_message": ["ClientCommunicationGuru"],
            "legal_research": ["LegalResearcher"],
            "case_law": ["LegalResearcher"],
            "schedule_appointment": ["VoiceScheduler"],
            "schedule_deposition": ["VoiceScheduler"],
            "schedule_mediation": ["VoiceScheduler"],
            "document_organization": ["EvidenceSorter"],
            "evidence_upload": ["EvidenceSorter"],
            "attachment_processing": ["EvidenceSorter"],
        }
    
    def _determine_target_agent(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Determine which agent should handle the task.
        
        Args:
            context: Task context
            
        Returns:
            Agent name or None if no suitable agent found
        """
        task_type = context.get("task_type", "").lower()
        
        # Direct routing based on task type
        if task_type in self.task_routing_rules:
            agent_names = self.task_routing_rules[task_type]
            if agent_names and agent_names[0] in self.sub_agents:
                return agent_names[0]
        
        # Fallback: analyze content for keywords
        content = context.get("content", "").lower()
        
        if any(keyword in content for keyword in ["medical", "records", "billing", "hospital", "doctor"]):
            return "RecordsWrangler"
        elif any(keyword in content for keyword in ["client", "message", "communication", "update"]):
            return "ClientCommunicationGuru"
        elif any(keyword in content for keyword in ["research", "case law", "precedent", "citation"]):
            return "LegalResearcher"
        elif any(keyword in content for keyword in ["schedule", "appointment", "deposition", "mediation"]):
            return "VoiceScheduler"
        elif any(keyword in content for keyword in ["document", "evidence", "attachment", "file"]):
            return "EvidenceSorter"
        
        self.logger.warning(f"No suitable agent found for task type: {task_type}")
        return None
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming task and route to appropriate specialist.
        
        Args:
            context: Task context containing:
                - task_type: Type of task
                - content: Task content/description
                - metadata: Additional metadata
                - requires_approval: Whether human approval is needed
                
        Returns:
            Result dictionary with:
                - status: success/error
                - agent: Agent that processed the task
                - result: Processing result
                - requires_approval: Whether approval is needed
        """
        self.log_action("Processing task", {"task_type": context.get("task_type")})
        
        # Validate input
        if not await self.validate_input(context):
            return {
                "status": "error",
                "error": "Invalid input context",
                "agent": self.name
            }
        
        # Determine target agent
        target_agent_name = self._determine_target_agent(context)
        
        if not target_agent_name:
            return {
                "status": "error",
                "error": "No suitable agent found for this task",
                "agent": self.name,
                "task_type": context.get("task_type")
            }
        
        # Get target agent
        target_agent = self.sub_agents.get(target_agent_name)
        
        if not target_agent:
            return {
                "status": "error",
                "error": f"Agent {target_agent_name} not registered",
                "agent": self.name
            }
        
        # Log routing decision
        self.log_action(
            "Routing task",
            {
                "target_agent": target_agent_name,
                "task_type": context.get("task_type")
            }
        )
        
        # Route to specialist agent
        try:
            result = await target_agent.process(context)
            
            # Add routing metadata
            result["routed_by"] = self.name
            result["agent"] = target_agent_name
            
            # Check if approval is required
            if context.get("requires_approval", True):
                result["requires_approval"] = True
                result["approval_status"] = "pending"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing task with {target_agent_name}: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent": target_agent_name,
                "routed_by": self.name
            }
    
    def get_available_agents(self) -> List[Dict[str, str]]:
        """
        Get list of available specialist agents.
        
        Returns:
            List of agent information dictionaries
        """
        return [agent.get_info() for agent in self.sub_agents.values()]
    
    def get_routing_rules(self) -> Dict[str, List[str]]:
        """
        Get current routing rules.
        
        Returns:
            Dictionary of routing rules
        """
        return self.task_routing_rules

