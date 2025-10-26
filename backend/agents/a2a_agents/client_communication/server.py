"""Client Communication Agent A2A Server"""
import os
import sys
import asyncio
import logging

import click
import uvicorn
from dotenv import load_dotenv

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agents.a2a_agents.client_communication.executor import ClientCommunicationExecutor
from agents.a2a_agents.client_communication.agent import ClientCommunicationAgent

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 10001
DEFAULT_LOG_LEVEL = 'info'


def get_agent_card(host: str, port: int) -> AgentCard:
    """Returns the Agent Card for the Client Communication Agent"""
    capabilities = AgentCapabilities(streaming=True, push_notifications=False)
    
    skills = [
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
    ]
    
    app_url = os.environ.get('APP_URL', f'http://{host}:{port}')
    
    return AgentCard(
        name='Client Communication Agent',
        description='Drafts clear, empathetic messages to clients. Serves as the gatekeeper before any messages go out to clients.',
        url=app_url,
        version='1.0.0',
        default_input_modes=ClientCommunicationAgent.SUPPORTED_CONTENT_TYPES,
        default_output_modes=ClientCommunicationAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=skills,
    )


def main(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    log_level: str = DEFAULT_LOG_LEVEL,
):
    """Start the Client Communication Agent server"""
    
    # Verify API key is set
    if not os.getenv('GEMINI_API_KEY'):
        raise ValueError('GEMINI_API_KEY environment variable not set')
    
    async def run_server_async():
        logger.info('Initializing Client Communication Agent server...')
        
        # Initialize executor
        executor = ClientCommunicationExecutor()
        
        # Create request handler
        request_handler = DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore(),
        )
        
        # Create A2A server
        a2a_server = A2AStarletteApplication(
            agent_card=get_agent_card(host, port),
            http_handler=request_handler,
        )
        
        # Get ASGI app
        asgi_app = a2a_server.build()
        
        # Configure uvicorn
        config = uvicorn.Config(
            app=asgi_app,
            host=host,
            port=port,
            log_level=log_level.lower(),
            lifespan='auto',
        )
        
        uvicorn_server = uvicorn.Server(config)
        
        logger.info(f'Starting Client Communication Agent server at http://{host}:{port}')
        try:
            await uvicorn_server.serve()
        except KeyboardInterrupt:
            logger.info('Server shutdown requested (KeyboardInterrupt).')
        finally:
            logger.info('Client Communication Agent server has stopped.')
    
    try:
        asyncio.run(run_server_async())
    except Exception as e:
        logger.error(f'Error in main: {e}', exc_info=True)
        sys.exit(1)


@click.command()
@click.option(
    '--host',
    'host',
    default=DEFAULT_HOST,
    help='Hostname to bind the server to.',
)
@click.option(
    '--port',
    'port',
    default=DEFAULT_PORT,
    type=int,
    help='Port to bind the server to.',
)
@click.option(
    '--log-level',
    'log_level',
    default=DEFAULT_LOG_LEVEL,
    help='Uvicorn log level.',
)
def cli(host: str, port: int, log_level: str):
    main(host, port, log_level)


if __name__ == '__main__':
    cli()

