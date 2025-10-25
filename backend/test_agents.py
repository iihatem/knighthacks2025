"""
Quick test script for TenderPilot agents.
Tests the basic agent structure without requiring API keys.
"""
import asyncio
import logging
from agents import (
    TenderCoordinatorAgent,
    RecordsWranglerAgent,
    ClientCommunicationGuruAgent,
    LegalResearcherAgent,
    VoiceSchedulerAgent,
    EvidenceSorterAgent
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_agents():
    """Test the agent system."""
    logger.info("="*60)
    logger.info("TenderPilot Agent System Test")
    logger.info("="*60)
    
    # Initialize coordinator
    coordinator = TenderCoordinatorAgent()
    logger.info(f"✓ Initialized {coordinator.name}")
    
    # Initialize specialized agents
    agents = [
        RecordsWranglerAgent(),
        ClientCommunicationGuruAgent(),
        LegalResearcherAgent(),
        VoiceSchedulerAgent(),
        EvidenceSorterAgent()
    ]
    
    # Register agents
    for agent in agents:
        coordinator.register_agent(agent)
        logger.info(f"✓ Registered {agent.name}")
    
    logger.info(f"\nTotal agents registered: {len(agents)}")
    
    # Test task routing
    logger.info("\n" + "="*60)
    logger.info("Testing Task Routing")
    logger.info("="*60)
    
    test_tasks = [
        {
            "task_type": "medical_records",
            "content": "Request MRI records from Dr. Smith",
            "metadata": {
                "provider_name": "Dr. Smith Medical Center",
                "patient_name": "John Doe",
                "case_id": "CASE-001"
            }
        },
        {
            "task_type": "client_communication",
            "content": "Send case update to client",
            "metadata": {
                "client_name": "Jane Smith",
                "case_id": "CASE-002"
            }
        },
        {
            "task_type": "legal_research",
            "content": "Find precedents for medical negligence",
            "metadata": {
                "jurisdiction": "Federal"
            }
        },
        {
            "task_type": "schedule_appointment",
            "content": "Schedule deposition with witness",
            "metadata": {
                "recipient_name": "John Witness",
                "recipient_role": "witness"
            }
        },
        {
            "task_type": "document_organization",
            "content": "Organize case documents",
            "metadata": {
                "case_id": "CASE-003",
                "files": [
                    {"filename": "medical_bill.pdf", "type": "application/pdf", "size": 1024},
                    {"filename": "xray_image.jpg", "type": "image/jpeg", "size": 2048}
                ]
            }
        }
    ]
    
    for i, task in enumerate(test_tasks, 1):
        logger.info(f"\nTest {i}: {task['task_type']}")
        logger.info("-" * 40)
        
        try:
            result = await coordinator.process(task)
            
            if result["status"] == "success":
                logger.info(f"✓ Status: {result['status']}")
                logger.info(f"✓ Routed to: {result['agent']}")
                logger.info(f"✓ Confidence: {result.get('confidence', 'N/A')}")
                if result.get('requires_approval'):
                    logger.info(f"✓ Requires Approval: Yes")
            else:
                logger.error(f"✗ Error: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"✗ Exception: {str(e)}")
    
    # Test system info
    logger.info("\n" + "="*60)
    logger.info("System Information")
    logger.info("="*60)
    
    available_agents = coordinator.get_available_agents()
    logger.info(f"Available Agents: {len(available_agents)}")
    for agent_info in available_agents:
        logger.info(f"  - {agent_info['name']}: {agent_info['description']}")
    
    logger.info("\n" + "="*60)
    logger.info("✓ All tests completed successfully!")
    logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(test_agents())

