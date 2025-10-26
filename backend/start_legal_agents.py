#!/usr/bin/env python3
"""
Legal AI A2A Agent Server Manager
Starts and keeps all legal AI A2A agents running continuously for frontend integration.
"""

import asyncio
import logging
import os
import sys
import threading
import time
import signal

import uvicorn
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import A2A components
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

# Import our agent executors
from agents.a2a_agents.client_communication.executor import ClientCommunicationExecutor
from agents.a2a_agents.client_communication.agent import ClientCommunicationAgent
from agents.a2a_agents.legal_researcher.executor import LegalResearcherExecutor
from agents.a2a_agents.legal_researcher.agent import LegalResearcherAgent
from agents.a2a_agents.records_wrangler.executor import RecordsWranglerExecutor
from agents.a2a_agents.records_wrangler.agent import RecordsWranglerAgent
from agents.a2a_agents.voice_scheduler.executor import VoiceSchedulerExecutor
from agents.a2a_agents.voice_scheduler.agent import VoiceSchedulerAgent
from agents.a2a_agents.evidence_sorter.executor import EvidenceSorterExecutor
from agents.a2a_agents.evidence_sorter.agent import EvidenceSorterAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LegalAgentManager:
    """Manages Legal AI A2A agent servers with proper threading and lifecycle management."""
    
    def __init__(self):
        self.executors = {}
        self.agent_cards = {}
        self.server_tasks = []
        self.running = False
        self.server_thread = None
        
    def setup_environment(self):
        """Setup environment variables and check prerequisites."""
        load_dotenv()
        
        # Check for required API key
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            logger.error("❌ Missing Gemini API Key!")
            logger.error("Please create a .env file with your GEMINI_API_KEY:")
            logger.error("GEMINI_API_KEY=your_actual_api_key_here")
            logger.error("Get your API key from: https://aistudio.google.com/apikey")
            return False
            
        logger.info("✅ Environment variables configured")
        logger.info(f"GEMINI_API_KEY: {'✅ Set' if gemini_api_key else '❌ Missing'}")
        return True
    
    def create_executors(self):
        """Create all legal agent executors."""
        try:
            self.executors = {
                'client_communication': ClientCommunicationExecutor(),
                'legal_researcher': LegalResearcherExecutor(),
                'records_wrangler': RecordsWranglerExecutor(),
                'voice_scheduler': VoiceSchedulerExecutor(),
                'evidence_sorter': EvidenceSorterExecutor(),
            }
            
            logger.info("✅ Legal agent executors created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create executors: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_agent_cards(self):
        """Create A2A Agent Cards for all legal agents."""
        try:
            self.agent_cards = {
                'client_communication': AgentCard(
                    name='Client Communication Agent',
                    url='http://localhost:10001',
                    description='Drafts clear, empathetic messages to clients. Serves as the gatekeeper before any messages go out to clients.',
                    version='1.0.0',
                    capabilities=AgentCapabilities(streaming=True, push_notifications=False),
                    default_input_modes=ClientCommunicationAgent.SUPPORTED_CONTENT_TYPES,
                    default_output_modes=ClientCommunicationAgent.SUPPORTED_CONTENT_TYPES,
                    skills=[
                        AgentSkill(
                            id='draft_email',
                            name='Draft Client Email',
                            description='Draft professional, empathetic emails to clients',
                            tags=['email', 'client communication', 'drafting'],
                            examples=[
                                'Draft an email to the client about their upcoming deposition',
                                'Write a message to the client explaining the settlement offer',
                                'Compose an email updating the client on case progress'
                            ],
                        ),
                        AgentSkill(
                            id='draft_message',
                            name='Draft Client Message',
                            description='Draft professional messages for clients',
                            tags=['message', 'client communication', 'drafting'],
                            examples=[
                                'Draft a message to the client about document requirements',
                                'Write a message explaining next steps in the case'
                            ],
                        ),
                    ],
                ),
                'legal_researcher': AgentCard(
                    name='Legal Researcher Agent',
                    url='http://localhost:10002',
                    description='Finds supporting verdicts, citations, and novel legal theories to strengthen cases',
                    version='1.0.0',
                    capabilities=AgentCapabilities(streaming=True, push_notifications=False),
                    default_input_modes=LegalResearcherAgent.SUPPORTED_CONTENT_TYPES,
                    default_output_modes=LegalResearcherAgent.SUPPORTED_CONTENT_TYPES,
                    skills=[
                        AgentSkill(
                            id='legal_research',
                            name='Legal Research',
                            description='Find relevant case law, precedents, and legal theories',
                            tags=['research', 'case law', 'precedents'],
                            examples=[
                                'Find precedents for personal injury cases involving medical malpractice',
                                'Research legal theories for wrongful termination case'
                            ],
                        ),
                    ],
                ),
                'records_wrangler': AgentCard(
                    name='Records Wrangler Agent',
                    url='http://localhost:10003',
                    description='Pulls missing bills or records from client messages and coordinates with medical providers',
                    version='1.0.0',
                    capabilities=AgentCapabilities(streaming=True, push_notifications=False),
                    default_input_modes=RecordsWranglerAgent.SUPPORTED_CONTENT_TYPES,
                    default_output_modes=RecordsWranglerAgent.SUPPORTED_CONTENT_TYPES,
                    skills=[
                        AgentSkill(
                            id='records_management',
                            name='Records Management',
                            description='Identify, request, and organize case records and documents',
                            tags=['records', 'documents', 'retrieval'],
                            examples=[
                                'Pull medical records from the client\'s last message',
                                'Request missing bills from the hospital',
                                'Identify what documents we still need for this case'
                            ],
                        ),
                    ],
                ),
                'voice_scheduler': AgentCard(
                    name='Voice Scheduler Agent',
                    url='http://localhost:10004',
                    description='Coordinates depositions, mediations, and client check-ins',
                    version='1.0.0',
                    capabilities=AgentCapabilities(streaming=True, push_notifications=False),
                    default_input_modes=VoiceSchedulerAgent.SUPPORTED_CONTENT_TYPES,
                    default_output_modes=VoiceSchedulerAgent.SUPPORTED_CONTENT_TYPES,
                    skills=[
                        AgentSkill(
                            id='appointment_scheduling',
                            name='Appointment Scheduling',
                            description='Schedule and coordinate legal proceedings and client meetings',
                            tags=['scheduling', 'appointments', 'calendar'],
                            examples=[
                                'Schedule a deposition for next week',
                                'Arrange a mediation session with opposing counsel',
                                'Set up a client check-in call'
                            ],
                        ),
                    ],
                ),
                'evidence_sorter': AgentCard(
                    name='Evidence Sorter Agent',
                    url='http://localhost:10005',
                    description='Extracts and labels attachments or media files from raw emails and organizes them',
                    version='1.0.0',
                    capabilities=AgentCapabilities(streaming=True, push_notifications=False),
                    default_input_modes=EvidenceSorterAgent.SUPPORTED_CONTENT_TYPES,
                    default_output_modes=EvidenceSorterAgent.SUPPORTED_CONTENT_TYPES,
                    skills=[
                        AgentSkill(
                            id='evidence_organization',
                            name='Evidence Organization',
                            description='Extract, classify, and organize case evidence and documents',
                            tags=['evidence', 'documents', 'organization'],
                            examples=[
                                'Sort and label the attachments from the client\'s email',
                                'Organize all medical records by date',
                                'Extract evidence from the latest correspondence'
                            ],
                        ),
                    ],
                ),
            }
            
            logger.info("✅ Agent cards created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create agent cards: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_agent_a2a_server(self, executor, agent_card):
        """Create an A2A server for an agent executor."""
        request_handler = DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore(),
        )

        return A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler
        )
    
    async def run_agent_server(self, agent_name: str, executor, agent_card, port: int):
        """Run a single agent server."""
        try:
            logger.info(f"🚀 Starting {agent_name} on port {port}")
            
            app = self.create_agent_a2a_server(executor, agent_card)
            
            config = uvicorn.Config(
                app.build(),
                host='0.0.0.0',
                port=port,
                log_level='warning',
                loop='none',
            )
            
            server = uvicorn.Server(config)
            await server.serve()
            
        except OSError as e:
            if e.errno == 48:  # Address already in use
                logger.error(f"❌ Port {port} is already in use for {agent_name}")
                logger.error(f"   Run: lsof -ti:{port} | xargs kill -9")
                logger.error(f"   Or run: ./kill_agent_ports.sh")
            else:
                logger.error(f"❌ OS Error running {agent_name}: {e}")
        except Exception as e:
            logger.error(f"❌ Error running {agent_name}: {e}")
            import traceback
            traceback.print_exc()
    
    async def start_all_servers(self):
        """Start all agent servers."""
        try:
            # Define agent configurations
            agent_configs = [
                ('client_communication', 10001),
                ('legal_researcher', 10002),
                ('records_wrangler', 10003),
                ('voice_scheduler', 10004),
                ('evidence_sorter', 10005),
            ]
            
            # Create tasks for all agents
            tasks = []
            for agent_name, port in agent_configs:
                if agent_name in self.executors and agent_name in self.agent_cards:
                    task = asyncio.create_task(
                        self.run_agent_server(
                            agent_name, 
                            self.executors[agent_name], 
                            self.agent_cards[agent_name], 
                            port
                        )
                    )
                    tasks.append(task)
            
            # Give servers time to start
            await asyncio.sleep(3)
            
            logger.info("=" * 60)
            logger.info("✅ All Legal AI A2A Agent Servers Started!")
            logger.info("=" * 60)
            logger.info("   📧 Client Communication: http://localhost:10001")
            logger.info("   📚 Legal Researcher:     http://localhost:10002")
            logger.info("   📁 Records Wrangler:     http://localhost:10003")
            logger.info("   📅 Voice Scheduler:      http://localhost:10004")
            logger.info("   🗂️  Evidence Sorter:      http://localhost:10005")
            logger.info("=" * 60)
            logger.info("🎯 Agents are now listening for frontend requests!")
            logger.info("💡 Use Ctrl+C to stop all servers")
            logger.info("=" * 60)
            
            # Keep servers running indefinitely
            self.running = True
            try:
                await asyncio.gather(*tasks)
            except KeyboardInterrupt:
                logger.info("\n🛑 Shutting down servers...")
                self.running = False
                
        except Exception as e:
            logger.error(f"❌ Error starting servers: {e}")
            import traceback
            traceback.print_exc()
            self.running = False
    
    def run_servers_in_background(self):
        """Run servers in a background thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.start_all_servers())
        except Exception as e:
            logger.error(f"❌ Background server error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            loop.close()
    
    def start(self):
        """Start the Legal Agent Manager."""
        logger.info("=" * 60)
        logger.info("🚀 Starting Legal AI A2A Agent Manager...")
        logger.info("=" * 60)
        
        # Setup environment
        if not self.setup_environment():
            return False
        
        # Create executors
        if not self.create_executors():
            return False
        
        # Create agent cards
        if not self.create_agent_cards():
            return False
        
        # Start servers in background thread
        self.server_thread = threading.Thread(target=self.run_servers_in_background, daemon=True)
        self.server_thread.start()
        
        # Wait for servers to be ready
        time.sleep(5)
        
        if self.running:
            logger.info("✅ Legal AI A2A Agent Manager started successfully!")
            return True
        else:
            logger.error("❌ Failed to start Legal AI A2A Agent Manager")
            return False
    
    def stop(self):
        """Stop the Legal Agent Manager."""
        logger.info("🛑 Stopping Legal AI A2A Agent Manager...")
        self.running = False
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)
        logger.info("✅ Legal AI A2A Agent Manager stopped")


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("\n🛑 Received shutdown signal...")
    if 'manager' in globals():
        manager.stop()
    sys.exit(0)


def main():
    """Main function to start the Legal AI A2A agent manager."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start manager
    global manager
    manager = LegalAgentManager()
    
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
        logger.error("❌ Failed to start Legal AI A2A Agent Manager")
        sys.exit(1)


if __name__ == "__main__":
    main()

