"""
TenderPilot Main Application.
Initializes and runs the multi-agent system.
"""
import logging
from typing import Dict, Any
from agents import (
    TenderCoordinatorAgent,
    RecordsWranglerAgent,
    ClientCommunicationGuruAgent,
    LegalResearcherAgent,
    VoiceSchedulerAgent,
    EvidenceSorterAgent
)
from config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TenderPilotApp:
    """
    Main TenderPilot application.
    Manages the multi-agent system and coordinates task processing.
    """
    
    def __init__(self):
        """Initialize the TenderPilot application."""
        logger.info("Initializing TenderPilot application...")
        
        # Validate configuration
        if not config.validate():
            logger.warning("Configuration validation failed. Some features may not work.")
        
        # Initialize coordinator
        self.coordinator = TenderCoordinatorAgent()
        
        # Initialize specialized agents
        self.agents = {
            "RecordsWrangler": RecordsWranglerAgent(),
            "ClientCommunicationGuru": ClientCommunicationGuruAgent(),
            "LegalResearcher": LegalResearcherAgent(),
            "VoiceScheduler": VoiceSchedulerAgent(),
            "EvidenceSorter": EvidenceSorterAgent()
        }
        
        # Register agents with coordinator
        for agent in self.agents.values():
            self.coordinator.register_agent(agent)
        
        logger.info(f"Initialized {len(self.agents)} specialized agents")
        logger.info("TenderPilot application ready")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task through the multi-agent system.
        
        Args:
            task: Task dictionary containing:
                - task_type: Type of task
                - content: Task content
                - metadata: Additional metadata
                - requires_approval: Whether approval is needed
                
        Returns:
            Processing result
        """
        logger.info(f"Processing task: {task.get('task_type')}")
        
        try:
            # Route task through coordinator
            result = await self.coordinator.process(task)
            
            logger.info(f"Task processed successfully by {result.get('agent')}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "task_type": task.get("task_type")
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the system and available agents.
        
        Returns:
            System information dictionary
        """
        return {
            "application": "TenderPilot",
            "version": "1.0.0",
            "coordinator": self.coordinator.get_info(),
            "available_agents": self.coordinator.get_available_agents(),
            "routing_rules": self.coordinator.get_routing_rules(),
            "total_agents": len(self.agents)
        }


# Global application instance
app = TenderPilotApp()


async def main():
    """Main entry point for testing."""
    logger.info("Starting TenderPilot...")
    
    # Print system info
    system_info = app.get_system_info()
    logger.info(f"System Info: {system_info['application']} v{system_info['version']}")
    logger.info(f"Available agents: {system_info['total_agents']}")
    
    # Example task processing
    test_tasks = [
        {
            "task_type": "medical_records",
            "content": "Need to request MRI records from Dr. Smith's office for patient John Doe",
            "metadata": {
                "provider_name": "Dr. Smith Medical Center",
                "patient_name": "John Doe",
                "case_id": "CASE-2025-001",
                "date_range": "January 2024 - March 2024"
            },
            "requires_approval": True
        },
        {
            "task_type": "client_communication",
            "content": "Send case update to client about settlement offer received",
            "metadata": {
                "client_name": "Jane Smith",
                "case_id": "CASE-2025-002",
                "attorney_name": "Attorney Johnson"
            },
            "requires_approval": True
        },
        {
            "task_type": "legal_research",
            "content": "Find precedents for medical negligence cases involving delayed diagnosis",
            "metadata": {
                "jurisdiction": "Federal",
                "case_type": "medical_malpractice"
            },
            "requires_approval": False
        }
    ]
    
    # Process test tasks
    for task in test_tasks:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {task['task_type']}")
        logger.info(f"{'='*60}")
        
        result = await app.process_task(task)
        
        logger.info(f"Status: {result['status']}")
        logger.info(f"Agent: {result.get('agent')}")
        if result.get('requires_approval'):
            logger.info(f"Requires Approval: Yes ({result.get('approval_type')})")
        logger.info(f"Confidence: {result.get('confidence', 'N/A')}")
    
    logger.info("\nTenderPilot test completed successfully!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

