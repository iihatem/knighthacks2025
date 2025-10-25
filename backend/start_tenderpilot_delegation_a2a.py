#!/usr/bin/env python3
"""
TenderPilot A2A Server with Delegation Routing
Implements proper delegation from coordinator to specialized agents.
"""

import asyncio
import logging
import os
import sys
import threading
import time
import signal
from typing import Dict, Any, List, Optional

import uvicorn
from dotenv import load_dotenv

# Import A2A components
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, TransportProtocol

# Import TenderPilot agents
from tenderpilot_agents import (
    tender_coordinator,
    records_wrangler,
    client_communication_guru,
    legal_researcher,
    voice_scheduler,
    evidence_sorter
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TenderPilotDelegationRouter:
    """Handles delegation routing from coordinator to specialized agents."""
    
    def __init__(self):
        self.coordinator = tender_coordinator
        self.specialized_agents = {
            "records_wrangler": records_wrangler,
            "client_communication_guru": client_communication_guru,
            "legal_researcher": legal_researcher,
            "voice_scheduler": voice_scheduler,
            "evidence_sorter": evidence_sorter
        }
        
        # Task type to agent mapping
        self.delegation_mapping = {
            "medical_records": "records_wrangler",
            "client_communication": "client_communication_guru",
            "legal_research": "legal_researcher",
            "schedule_appointment": "voice_scheduler",
            "document_organization": "evidence_sorter"
        }
        
        # Approval requirements
        self.approval_required_tasks = [
            "client_communication",
            "settlement_discussion",
            "high_value_negotiation"
        ]
    
    async def route_task(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route task from coordinator to appropriate specialized agent.
        
        Args:
            task_context: Task context containing task details
            
        Returns:
            Routing result with delegation information
        """
        task_type = task_context.get("task_type", "unknown")
        
        logger.info(f"Routing task: {task_type}")
        
        # Check if task type is supported
        if task_type not in self.delegation_mapping:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}",
                "supported_types": list(self.delegation_mapping.keys())
            }
        
        # Get target agent
        target_agent_name = self.delegation_mapping[task_type]
        target_agent = self.specialized_agents[target_agent_name]
        
        # Check if approval is required
        requires_approval = task_type in self.approval_required_tasks
        
        # Simulate delegation
        delegation_result = {
            "status": "success",
            "task_type": task_type,
            "target_agent": target_agent_name,
            "agent_name": target_agent.name,
            "agent_model": target_agent.model,
            "agent_tools": len(target_agent.tools),
            "requires_approval": requires_approval,
            "confidence": 0.90,
            "delegation_timestamp": time.time(),
            "routing_reasoning": f"Task '{task_type}' delegated to {target_agent_name} based on task analysis"
        }
        
        logger.info(f"✓ Delegated to {target_agent_name} (approval: {requires_approval})")
        
        return delegation_result
    
    async def process_delegated_task(self, agent_name: str, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process task with the delegated specialized agent.
        
        Args:
            agent_name: Name of the specialized agent
            task_context: Task context to process
            
        Returns:
            Processing result from the specialized agent
        """
        if agent_name not in self.specialized_agents:
            return {
                "status": "error",
                "message": f"Agent {agent_name} not found",
                "available_agents": list(self.specialized_agents.keys())
            }
        
        agent = self.specialized_agents[agent_name]
        
        logger.info(f"Processing with {agent_name}: {agent.name}")
        
        # Simulate agent processing
        processing_result = {
            "status": "success",
            "agent_name": agent_name,
            "agent_model": agent.model,
            "task_context": task_context,
            "processing_result": f"Task processed by {agent.name} using {agent.model}",
            "tools_available": [tool.__name__ for tool in agent.tools],
            "confidence": 0.85,
            "processing_timestamp": time.time()
        }
        
        # Add specific processing based on agent type
        if agent_name == "records_wrangler":
            processing_result["specific_result"] = "Medical records request processed"
        elif agent_name == "client_communication_guru":
            processing_result["specific_result"] = "Client message drafted with empathetic tone"
        elif agent_name == "legal_researcher":
            processing_result["specific_result"] = "Legal research completed with precedents"
        elif agent_name == "voice_scheduler":
            processing_result["specific_result"] = "Appointment scheduled via voice call"
        elif agent_name == "evidence_sorter":
            processing_result["specific_result"] = "Documents categorized and organized"
        
        logger.info(f"✓ {agent_name} processing completed")
        
        return processing_result
    
    async def handle_approval_request(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle human approval request for tasks requiring approval.
        
        Args:
            task_context: Task context requiring approval
            
        Returns:
            Approval handling result
        """
        task_type = task_context.get("task_type", "unknown")
        
        logger.info(f"Handling approval request for: {task_type}")
        
        approval_result = {
            "status": "pending_approval",
            "task_type": task_type,
            "approval_required": True,
            "approval_message": f"Human approval required for {task_type} task",
            "approval_timestamp": time.time(),
            "next_steps": [
                "Send approval request to human reviewer",
                "Wait for approval decision",
                "Process approved task",
                "Notify completion"
            ]
        }
        
        logger.info(f"✓ Approval request created for {task_type}")
        
        return approval_result


class TenderPilotDelegationA2AServer:
    """A2A Server with delegation routing capabilities."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8001):
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        self.router = TenderPilotDelegationRouter()
        self.running = False
        
    def setup_environment(self):
        """Setup environment variables."""
        load_dotenv()
        
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            self.logger.error("❌ Missing Google API Key!")
            return False
            
        self.logger.info("✅ Environment configured")
        return True
    
    def create_agent_cards(self):
        """Create A2A Agent Cards for delegation."""
        try:
            self.agent_cards = {
                'tender_coordinator': AgentCard(
                    name='TenderPilot Legal Orchestrator',
                    url=f'http://{self.host}:{self.port}',
                    description='AI-powered legal tender orchestrator with delegation routing',
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['text/plain'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id='delegate_legal_tasks',
                            name='Delegate Legal Tasks',
                            description='Routes legal tasks to appropriate specialized agents',
                            tags=['delegation', 'routing', 'orchestration', 'legal'],
                            examples=[
                                'Route medical records request to Records Wrangler',
                                'Delegate client communication to Communication Guru',
                                'Assign legal research to Legal Researcher'
                            ],
                        )
                    ],
                )
            }
            
            # Create cards for specialized agents
            agent_ports = {
                "records_wrangler": 10031,
                "client_communication_guru": 10032,
                "legal_researcher": 10033,
                "voice_scheduler": 10034,
                "evidence_sorter": 10035
            }
            
            for agent_name, agent_instance in self.router.specialized_agents.items():
                port = agent_ports.get(agent_name, 10030)
                self.agent_cards[agent_name] = AgentCard(
                    name=agent_instance.name,
                    url=f'http://{self.host}:{port}',
                    description=agent_instance.description,
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['text/plain'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id=f'process_{agent_name}_tasks',
                            name=f'Process {agent_name.replace("_", " ").title()} Tasks',
                            description=f'Processes tasks delegated from coordinator',
                            tags=['specialized', 'processing', 'legal'],
                            examples=[f'Process {agent_name} task delegated from coordinator'],
                        )
                    ],
                )
            
            self.logger.info("✅ Agent cards created for delegation")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create agent cards: {e}")
            return False
    
    async def simulate_delegation_workflow(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate complete delegation workflow.
        
        Args:
            task_context: Task context to process
            
        Returns:
            Complete workflow result
        """
        self.logger.info(f"Starting delegation workflow for: {task_context.get('task_type', 'unknown')}")
        
        # Step 1: Route task
        routing_result = await self.router.route_task(task_context)
        
        if routing_result["status"] != "success":
            return routing_result
        
        # Step 2: Check if approval is required
        if routing_result["requires_approval"]:
            approval_result = await self.router.handle_approval_request(task_context)
            return {
                "status": "pending_approval",
                "routing": routing_result,
                "approval": approval_result,
                "workflow_status": "waiting_for_approval"
            }
        
        # Step 3: Process with specialized agent
        processing_result = await self.router.process_delegated_task(
            routing_result["target_agent"],
            task_context
        )
        
        # Step 4: Combine results
        workflow_result = {
            "status": "completed",
            "routing": routing_result,
            "processing": processing_result,
            "workflow_status": "completed",
            "total_confidence": routing_result["confidence"] * processing_result["confidence"]
        }
        
        self.logger.info(f"✓ Delegation workflow completed with confidence: {workflow_result['total_confidence']}")
        
        return workflow_result
    
    def start(self):
        """Start the delegation A2A server."""
        self.logger.info("🚀 Starting TenderPilot Delegation A2A Server...")
        
        # Setup environment
        if not self.setup_environment():
            return False
        
        # Create agent cards
        if not self.create_agent_cards():
            return False
        
        # Mark as running
        self.running = True
        
        self.logger.info("✅ TenderPilot Delegation A2A Server started!")
        self.logger.info(f"🎯 Coordinator: {self.router.coordinator.name}")
        self.logger.info(f"🤖 Specialized Agents: {len(self.router.specialized_agents)}")
        self.logger.info(f"📋 Agent Cards: {len(self.agent_cards)}")
        
        # Display delegation mapping
        self.logger.info("\n🔄 Delegation Mapping:")
        for task_type, agent_name in self.router.delegation_mapping.items():
            self.logger.info(f"   {task_type} → {agent_name}")
        
        # Display approval requirements
        self.logger.info(f"\n👤 Approval Required Tasks: {self.router.approval_required_tasks}")
        
        self.logger.info("\n🚀 Ready for delegation testing!")
        self.logger.info("💡 Use test_agent_delegation.py to test delegation")
        
        return True
    
    def stop(self):
        """Stop the delegation A2A server."""
        self.logger.info("🛑 Stopping TenderPilot Delegation A2A Server...")
        self.running = False
        self.logger.info("✅ Server stopped")


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("📡 Received shutdown signal...")
    if 'server' in globals():
        server.stop()
    sys.exit(0)


def main():
    """Main function to start the delegation A2A server."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start server
    global server
    server = TenderPilotDelegationA2AServer()
    
    if server.start():
        try:
            # Keep server running
            while server.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            server.stop()
    else:
        logger.error("❌ Failed to start TenderPilot Delegation A2A Server")
        sys.exit(1)


if __name__ == "__main__":
    main()
