#!/usr/bin/env python3
"""
A2A Agent Server Manager
Starts and keeps all A2A agents running continuously for frontend integration.
"""

import asyncio
import logging
import os
import sys
import threading
import time
import signal
from typing import List

import uvicorn
from dotenv import load_dotenv

# Import A2A components
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, TransportProtocol
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

# Import Google ADK components
from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor, A2aAgentExecutorConfig
from google.adk.agents import Agent, SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search

# Import existing ADK agents
from adk_agents.secretary.agent import root_agent as secretary_base_agent
from adk_agents.hiring_manager.agent import root_agent as hiring_manager_base_agent
from adk_agents.data_analyst.agent import root_agent as data_analyst_base_agent
from adk_agents.researcher.agent import root_agent as researcher_base_agent
from adk_agents.content_creator.agent import root_agent as content_creator_base_agent
from adk_agents.adk_agent_builder_assistant.agent import root_agent as agent_builder_base_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class A2AAgentManager:
    """Manages A2A agent servers with proper threading and lifecycle management."""
    
    def __init__(self):
        self.agents = {}
        self.agent_cards = {}
        self.server_tasks = []
        self.running = False
        self.server_thread = None
        
    def setup_environment(self):
        """Setup environment variables and check prerequisites."""
        load_dotenv()
        
        # Set Google Cloud Configuration
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'FALSE')
        os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id')
        os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        
        # Check for required API key
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            logger.error("❌ Missing Google API Key!")
            logger.error("Please create a .env file with your GOOGLE_API_KEY:")
            logger.error("GOOGLE_API_KEY=your_actual_api_key_here")
            logger.error("Get your API key from: https://aistudio.google.com/apikey")
            return False
            
        logger.info(" Environment variables configured")
        logger.info(f"GOOGLE_API_KEY: {' Set' if google_api_key else '❌ Missing'}")
        return True
    
    def create_agents(self):
        """Create all platform agents."""
        try:
            # Use existing ADK agents from the platform
            self.agents = {
                'secretary': secretary_base_agent,
                'hiring_manager': hiring_manager_base_agent,
                'data_analyst': data_analyst_base_agent,
                'researcher': researcher_base_agent,
                'content_creator': content_creator_base_agent,
                'agent_builder': agent_builder_base_agent,
            }
            
            logger.info(" Platform agents loaded successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load agents: {e}")
            return False
    
    def create_agent_cards(self):
        """Create A2A Agent Cards for all agents."""
        try:
            self.agent_cards = {
                'secretary': AgentCard(
                    name='Secretary Agent',
                    url='http://localhost:10020',
                    description='Main orchestrator that coordinates and delegates tasks to specialized employee agents',
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['text/plain'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id='coordinate_tasks',
                            name='Coordinate Tasks',
                            description='Understands user requests and routes them to appropriate specialists',
                            tags=['coordination', 'routing', 'assistance', 'guidance'],
                            examples=[
                                'I need help with data analysis',
                                'Can you help me create content for my blog?',
                                'What can this platform do?',
                            ],
                        )
                    ],
                ),
                'hiring_manager': AgentCard(
                    name='Hiring Manager Agent',
                    url='http://localhost:10021',
                    description='Creates and manages new employee agents based on organizational needs',
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['text/plain'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id='create_agents',
                            name='Create New Agents',
                            description='Analyzes needs and creates specialized agents with specific capabilities',
                            tags=['agent creation', 'specialization', 'management', 'workforce'],
                            examples=[
                                'I need a specialized marketing agent',
                                'Create an agent for financial analysis',
                                'We need more research capabilities',
                            ],
                        )
                    ],
                ),
                'data_analyst': AgentCard(
                    name='Data Analyst Agent',
                    url='http://localhost:10022',
                    description='Analyzes data, generates insights, and creates statistical reports',
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['application/json'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id='analyze_data',
                            name='Analyze Data',
                            description='Performs statistical analysis, identifies patterns, and generates insights',
                            tags=['data analysis', 'statistics', 'insights', 'reporting', 'trends'],
                            examples=[
                                'Analyze this sales data for trends',
                                'Generate a statistical report on user behavior',
                                'What patterns do you see in this dataset?',
                            ],
                        )
                    ],
                ),
                'researcher': AgentCard(
                    name='Researcher Agent',
                    url='http://localhost:10023',
                    description='Conducts comprehensive research, fact-checking, and information synthesis',
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['text/plain'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id='conduct_research',
                            name='Conduct Research',
                            description='Performs thorough research, fact-checking, and information gathering',
                            tags=['research', 'fact-checking', 'information', 'sources', 'verification'],
                            examples=[
                                'Research the latest developments in AI',
                                'Fact-check this information about climate change',
                                'Find authoritative sources on renewable energy',
                            ],
                        )
                    ],
                ),
                'content_creator': AgentCard(
                    name='Content Creator Agent',
                    url='http://localhost:10024',
                    description='Creates engaging content, marketing copy, and creative communications',
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['text/plain'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id='create_content',
                            name='Create Content',
                            description='Writes blog posts, marketing copy, social media content, and creative communications',
                            tags=['content creation', 'writing', 'marketing', 'social media', 'creative'],
                            examples=[
                                'Write a blog post about sustainable technology',
                                'Create social media content for our product launch',
                                'Help me improve this marketing copy',
                            ],
                        )
                    ],
                ),
                'agent_builder': AgentCard(
                    name='Agent Builder Assistant',
                    url='http://localhost:10026',
                    description='Intelligent assistant for building ADK multi-agent systems using YAML configurations',
                    version='1.0',
                    capabilities=AgentCapabilities(streaming=True),
                    default_input_modes=['text/plain'],
                    default_output_modes=['text/plain'],
                    preferred_transport=TransportProtocol.jsonrpc,
                    skills=[
                        AgentSkill(
                            id='build_agents',
                            name='Build Agent Systems',
                            description='Creates and configures ADK multi-agent systems with YAML configurations',
                            tags=['agent building', 'system design', 'yaml configuration', 'multi-agent', 'architecture'],
                            examples=[
                                'Help me build a multi-agent system for customer support',
                                'Create a YAML configuration for a data processing pipeline',
                                'Design an agent architecture for content management',
                            ],
                        )
                    ],
                ),
            }
            
            logger.info(" Agent cards created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create agent cards: {e}")
            return False
    
    def create_agent_a2a_server(self, agent, agent_card):
        """Create an A2A server for any ADK agent."""
        runner = Runner(
            app_name=agent.name,
            agent=agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

        config = A2aAgentExecutorConfig()
        executor = A2aAgentExecutor(runner=runner, config=config)

        request_handler = DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore(),
        )

        return A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )
    
    async def run_agent_server(self, agent_name: str, agent, agent_card, port: int):
        """Run a single agent server."""
        try:
            logger.info(f" Starting {agent_name} agent on port {port}")
            
            app = self.create_agent_a2a_server(agent, agent_card)
            
            config = uvicorn.Config(
                app.build(),
                host='127.0.0.1',
                port=port,
                log_level='warning',
                loop='none',
            )
            
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            logger.error(f"❌ Error running {agent_name} agent: {e}")
    
    async def start_all_servers(self):
        """Start all agent servers."""
        try:
            # Define agent configurations
            agent_configs = [
                ('secretary', 10020),
                ('hiring_manager', 10021),
                ('data_analyst', 10022),
                ('researcher', 10023),
                ('content_creator', 10024),
                ('agent_builder', 10026),
            ]
            
            # Create tasks for all agents
            tasks = []
            for agent_name, port in agent_configs:
                if agent_name in self.agents and agent_name in self.agent_cards:
                    task = asyncio.create_task(
                        self.run_agent_server(
                            agent_name, 
                            self.agents[agent_name], 
                            self.agent_cards[agent_name], 
                            port
                        )
                    )
                    tasks.append(task)
            
            # Give servers time to start
            await asyncio.sleep(3)
            
            logger.info(" All A2A agent servers started!")
            logger.info("   - Secretary Agent: http://127.0.0.1:10020")
            logger.info("   - Hiring Manager Agent: http://127.0.0.1:10021")
            logger.info("   - Data Analyst Agent: http://127.0.0.1:10022")
            logger.info("   - Researcher Agent: http://127.0.0.1:10023")
            logger.info("   - Content Creator Agent: http://127.0.0.1:10024")
            logger.info("   - Agent Builder Assistant: http://127.0.0.1:10026")
            logger.info("")
            logger.info(" Agents are now listening for frontend requests!")
            logger.info("💡 Use Ctrl+C to stop all servers")
            
            # Keep servers running indefinitely
            self.running = True
            try:
                await asyncio.gather(*tasks)
            except KeyboardInterrupt:
                logger.info(" Shutting down servers...")
                self.running = False
                
        except Exception as e:
            logger.error(f"❌ Error starting servers: {e}")
            self.running = False
    
    def run_servers_in_background(self):
        """Run servers in a background thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.start_all_servers())
        except Exception as e:
            logger.error(f"❌ Background server error: {e}")
        finally:
            loop.close()
    
    def start(self):
        """Start the A2A agent manager."""
        logger.info(" Starting A2A Agent Manager...")
        
        # Setup environment
        if not self.setup_environment():
            return False
        
        # Create agents
        if not self.create_agents():
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
            logger.info(" A2A Agent Manager started successfully!")
            return True
        else:
            logger.error("❌ Failed to start A2A Agent Manager")
            return False
    
    def stop(self):
        """Stop the A2A agent manager."""
        logger.info(" Stopping A2A Agent Manager...")
        self.running = False
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)
        logger.info(" A2A Agent Manager stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(" Received shutdown signal...")
    if 'manager' in globals():
        manager.stop()
    sys.exit(0)

def main():
    """Main function to start the A2A agent manager."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start manager
    global manager
    manager = A2AAgentManager()
    
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
        logger.error("❌ Failed to start A2A Agent Manager")
        sys.exit(1)

if __name__ == "__main__":
    main()
