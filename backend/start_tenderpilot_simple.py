#!/usr/bin/env python3
"""
TenderPilot Simple A2A Agent Server Manager
Simplified version that focuses on core functionality without complex imports.
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

# Import our TenderPilot ADK agents
from adk_agents import (
    get_tender_coordinator,
    get_specialized_agents,
    get_workflow_agents,
    get_agent_tools
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TenderPilotSimpleA2AManager:
    """Simplified TenderPilot A2A agent manager that focuses on core functionality."""
    
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
        """Create all TenderPilot agents."""
        try:
            # Get the main coordinator
            coordinator = get_tender_coordinator()
            specialized_agents = get_specialized_agents()
            workflow_agents = get_workflow_agents()
            
            # Create agent dictionary
            self.agents = {
                'tender_coordinator': coordinator,
                'records_wrangler': specialized_agents[0],  # RecordsWrangler
                'client_communication_guru': specialized_agents[1],  # ClientCommunicationGuru
                'legal_researcher': specialized_agents[2],  # LegalResearcher
                'voice_scheduler': specialized_agents[3],  # VoiceScheduler
                'evidence_sorter': specialized_agents[4],  # EvidenceSorter
                'case_processing_pipeline': workflow_agents[0],  # CaseProcessingPipeline
                'information_gatherer': workflow_agents[1],  # InformationGatherer
                'client_communication_workflow': workflow_agents[2],  # ClientCommunicationWorkflow
                'legal_research_loop': workflow_agents[3],  # LegalResearchLoop
            }
            
            logger.info("✅ TenderPilot agents loaded successfully")
            logger.info(f"   Total agents: {len(self.agents)}")
            for name, agent in self.agents.items():
                logger.info(f"   - {name}: {agent.name}")
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
                'legal_researcher': AgentCard(
                    name='Legal Researcher Agent',
                    url='http://localhost:10033',
                    description='Finds case law, precedents, and legal citations to strengthen cases',
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['text/plain'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id='legal_research',
                            name='Legal Research',
                            description='Finds case law, precedents, and legal citations',
                            tags=['research', 'legal', 'precedent', 'case law'],
                            examples=[
                                'Find precedents for medical negligence',
                                'Research case law for settlement',
                                'Find supporting legal citations',
                            ],
                        )
                    ],
                ),
                'voice_scheduler': AgentCard(
                    name='Voice Scheduler Agent',
                    url='http://localhost:10034',
                    description='Coordinates appointments via voice calls using ElevenLabs',
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['text/plain'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id='appointment_scheduling',
                            name='Appointment Scheduling',
                            description='Schedules appointments via voice calls',
                            tags=['scheduling', 'voice', 'appointment', 'elevenlabs'],
                            examples=[
                                'Schedule deposition with witness',
                                'Book medical appointment',
                                'Coordinate mediation scheduling',
                            ],
                        )
                    ],
                ),
                'evidence_sorter': AgentCard(
                    name='Evidence Sorter Agent',
                    url='http://localhost:10035',
                    description='Organizes documents, evidence, and attachments for case management',
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['text/plain'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id='document_organization',
                            name='Document Organization',
                            description='Organizes and categorizes case documents',
                            tags=['documents', 'organization', 'evidence', 'case management'],
                            examples=[
                                'Organize case files',
                                'Categorize evidence',
                                'Sort medical documents',
                            ],
                        )
                    ],
                ),
            }
            
            logger.info("✅ Agent cards created successfully")
            logger.info(f"   Total agent cards: {len(self.agent_cards)}")
            for name, card in self.agent_cards.items():
                logger.info(f"   - {name}: {card.name} at {card.url}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create agent cards: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "manager": "TenderPilot Simple A2A Manager",
            "version": "1.0.0",
            "agents": len(self.agents),
            "agent_cards": len(self.agent_cards),
            "running": self.running
        }
    
    def start(self):
        """Start the TenderPilot A2A agent manager."""
        logger.info("🚀 Starting TenderPilot Simple A2A Agent Manager...")
        
        # Setup environment
        if not self.setup_environment():
            return False
        
        # Create agents
        if not self.create_agents():
            return False
        
        # Create agent cards
        if not self.create_agent_cards():
            return False
        
        # Mark as running
        self.running = True
        
        logger.info("✅ TenderPilot Simple A2A Agent Manager started successfully!")
        logger.info("🎉 All agents and agent cards are ready!")
        
        # Display system info
        system_info = self.get_system_info()
        logger.info(f"📊 System Info: {system_info}")
        
        return True
    
    def stop(self):
        """Stop the TenderPilot A2A agent manager."""
        logger.info("🛑 Stopping TenderPilot Simple A2A Agent Manager...")
        self.running = False
        logger.info("✅ TenderPilot Simple A2A Agent Manager stopped")


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
    manager = TenderPilotSimpleA2AManager()
    
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
        logger.error("❌ Failed to start TenderPilot A2A Agent Manager")
        sys.exit(1)


if __name__ == "__main__":
    main()
