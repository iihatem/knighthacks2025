#!/usr/bin/env python3
"""
TenderPilot Proper A2A Agent Server Manager
Uses the properly structured Google ADK agents from tenderpilot_agents package.
"""

import asyncio
import logging
import os
import sys
import threading
import time
import signal
from typing import List, Dict, Any

import uvicorn
from dotenv import load_dotenv

# Import A2A components (simplified)
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, TransportProtocol

# Import our properly structured TenderPilot agents
from tenderpilot_agents import (
    tender_coordinator,
    records_wrangler,
    client_communication_guru
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TenderPilotProperA2AManager:
    """TenderPilot A2A agent manager using properly structured Google ADK agents."""
    
    def __init__(self):
        self.agents = {}
        self.agent_cards = {}
        self.running = False
        self.server_thread = None
        
    def setup_environment(self):
        """Setup environment variables and check prerequisites."""
        load_dotenv()
        
        # Check for required API key
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            logger.error("❌ Missing Google API Key!")
            logger.error("Please create a .env file with your GOOGLE_API_KEY:")
            logger.error("GOOGLE_API_KEY=your_actual_api_key_here")
            logger.error("Get your API key from: https://aistudio.google.com/apikey")
            return False
            
        logger.info("✅ Environment variables configured")
        logger.info(f"GOOGLE_API_KEY: {'✅ Set' if google_api_key else '❌ Missing'}")
        return True
    
    def create_agents(self):
        """Create all TenderPilot agents using the properly structured package."""
        try:
            # Use the properly structured agents from tenderpilot_agents package
            self.agents = {
                'tender_coordinator': tender_coordinator,
                'records_wrangler': records_wrangler,
                'client_communication_guru': client_communication_guru,
            }
            
            logger.info("✅ TenderPilot agents loaded from proper Google ADK structure")
            logger.info(f"   Total agents: {len(self.agents)}")
            for name, agent in self.agents.items():
                logger.info(f"   - {name}: {agent.name}")
                logger.info(f"     Model: {agent.model}")
                logger.info(f"     Tools: {len(agent.tools)}")
                for tool in agent.tools:
                    logger.info(f"       - {tool.__name__}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load agents: {e}")
            return False
    
    def create_agent_cards(self):
        """Create A2A Agent Cards for all TenderPilot agents."""
        try:
            self.agent_cards = {
                'tender_coordinator': AgentCard(
                    name='TenderPilot Legal Orchestrator',
                    url='http://localhost:10030',
                    description='AI-powered legal tender orchestrator for Morgan & Morgan that routes tasks to specialized agents',
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['text/plain'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id='legal_task_orchestration',
                            name='Legal Task Orchestration',
                            description='Orchestrates legal tasks and routes them to specialized agents',
                            tags=['legal', 'orchestration', 'routing', 'coordination'],
                            examples=[
                                'Process this medical records request',
                                'Route this client communication task',
                                'Coordinate legal research for this case',
                            ],
                        )
                    ],
                ),
                'records_wrangler': AgentCard(
                    name='Records Wrangler Agent',
                    url='http://localhost:10031',
                    description='Handles medical records and billing requests from providers',
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['text/plain'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id='medical_records_retrieval',
                            name='Medical Records Retrieval',
                            description='Requests and tracks medical records from providers',
                            tags=['medical', 'records', 'billing', 'providers'],
                            examples=[
                                'Get MRI records from Dr. Smith',
                                'Request billing from hospital',
                                'Track medical record fulfillment',
                            ],
                        )
                    ],
                ),
                'client_communication_guru': AgentCard(
                    name='Client Communication Guru',
                    url='http://localhost:10032',
                    description='Drafts clear, empathetic messages to clients and reviews outgoing communications',
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['text/plain'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id='client_message_drafting',
                            name='Client Message Drafting',
                            description='Drafts empathetic and clear messages to clients',
                            tags=['communication', 'client', 'message', 'empathy'],
                            examples=[
                                'Draft case update for client',
                                'Send settlement notification',
                                'Create empathetic client message',
                            ],
                        )
                    ],
                ),
            }
            
            logger.info("✅ Agent cards created successfully")
            logger.info(f"   Total agent cards: {len(self.agent_cards)}")
            for name, card in self.agent_cards.items():
                logger.info(f"   - {name}: {card.name} at {card.url}")
                logger.info(f"     Skills: {len(card.skills)}")
                for skill in card.skills:
                    logger.info(f"       - {skill.name}: {skill.description}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create agent cards: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "manager": "TenderPilot Proper A2A Manager",
            "version": "1.0.0",
            "agents": len(self.agents),
            "agent_cards": len(self.agent_cards),
            "running": self.running,
            "structure": "Proper Google ADK Structure"
        }
    
    def test_agent_tools(self):
        """Test agent tools functionality."""
        logger.info("\n" + "="*60)
        logger.info("Testing Agent Tools from Proper Structure")
        logger.info("="*60)
        
        try:
            # Test Records Wrangler tools
            logger.info("\nTesting Records Wrangler Tools...")
            from tenderpilot_agents.records_wrangler.utils import (
                request_medical_records,
                generate_provider_letter
            )
            
            # Test medical records request
            result = request_medical_records(
                provider_name="Dr. Smith Medical Center",
                patient_name="John Doe",
                record_types=["MRI", "Lab Results", "Billing"]
            )
            logger.info(f"✓ Medical records request: {result['status']}")
            
            # Test provider letter generation
            letter_result = generate_provider_letter(
                provider_name="Dr. Smith Medical Center",
                patient_name="John Doe",
                record_types=["MRI", "Lab Results"]
            )
            logger.info(f"✓ Provider letter generation: {letter_result['status']}")
            
            # Test Client Communication Guru tools
            logger.info("\nTesting Client Communication Guru Tools...")
            from tenderpilot_agents.client_communication_guru.utils import (
                draft_client_message,
                get_tone_guidelines
            )
            
            # Test message drafting
            message_result = draft_client_message(
                client_name="Jane Smith",
                message_type="case_update",
                context={"message_body": "Your case is progressing well", "next_steps": "We'll update you next week"}
            )
            logger.info(f"✓ Client message drafting: {message_result['status']}")
            
            # Test tone guidelines
            guidelines = get_tone_guidelines("bad_news")
            logger.info(f"✓ Tone guidelines: {guidelines['tone']}")
            
            # Test TenderPilot Coordinator tools
            logger.info("\nTesting TenderPilot Coordinator Tools...")
            from tenderpilot_agents.tender_coordinator.utils import (
                route_task_to_agent,
                check_approval_required
            )
            
            # Test task routing
            routing_result = route_task_to_agent(
                task_type="medical_records",
                task_data={"patient": "John Doe", "provider": "Dr. Smith"}
            )
            logger.info(f"✓ Task routing: {routing_result['status']}")
            
            # Test approval checking
            approval_result = check_approval_required(
                task_type="settlement_discussion",
                task_data={"amount": 50000, "priority": "high"}
            )
            logger.info(f"✓ Approval check: {approval_result['status']}")
            
            logger.info("\n" + "="*60)
            logger.info("✅ All agent tools from proper structure working!")
            logger.info("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Agent tools test failed: {e}")
            return False
    
    def start(self):
        """Start the TenderPilot A2A agent manager."""
        logger.info("🚀 Starting TenderPilot Proper A2A Agent Manager...")
        logger.info("📦 Using properly structured Google ADK agents from tenderpilot_agents package")
        
        # Setup environment
        if not self.setup_environment():
            return False
        
        # Create agents from proper structure
        if not self.create_agents():
            return False
        
        # Create agent cards
        if not self.create_agent_cards():
            return False
        
        # Test agent tools
        if not self.test_agent_tools():
            logger.warning("⚠️ Some agent tools failed, but continuing...")
        
        # Mark as running
        self.running = True
        
        logger.info("✅ TenderPilot Proper A2A Agent Manager started successfully!")
        logger.info("🎉 All agents and agent cards are ready!")
        
        # Display system info
        system_info = self.get_system_info()
        logger.info(f"📊 System Info: {system_info}")
        
        logger.info("\n" + "="*60)
        logger.info("🎯 TenderPilot Agents Ready for A2A Integration!")
        logger.info("="*60)
        logger.info("📋 Available Agents:")
        for name, agent in self.agents.items():
            logger.info(f"   - {name}: {agent.name} ({agent.model})")
            logger.info(f"     Tools: {len(agent.tools)}")
        
        logger.info("\n📋 Available Agent Cards:")
        for name, card in self.agent_cards.items():
            logger.info(f"   - {name}: {card.name}")
            logger.info(f"     URL: {card.url}")
            logger.info(f"     Skills: {len(card.skills)}")
        
        logger.info("\n🚀 Ready for A2A server integration!")
        logger.info("💡 Use Ctrl+C to stop the manager")
        
        return True
    
    def stop(self):
        """Stop the TenderPilot A2A agent manager."""
        logger.info("🛑 Stopping TenderPilot Proper A2A Agent Manager...")
        self.running = False
        logger.info("✅ TenderPilot Proper A2A Agent Manager stopped")


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("📡 Received shutdown signal...")
    if 'manager' in globals():
        manager.stop()
    sys.exit(0)


def main():
    """Main function to start the TenderPilot A2A agent manager."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start manager
    global manager
    manager = TenderPilotProperA2AManager()
    
    if manager.start():
        try:
            # Keep main thread alive
            while manager.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            manager.stop()
    else:
        logger.error("❌ Failed to start TenderPilot Proper A2A Agent Manager")
        sys.exit(1)


if __name__ == "__main__":
    main()
