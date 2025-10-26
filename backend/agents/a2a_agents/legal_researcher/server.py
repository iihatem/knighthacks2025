"""Legal Researcher Agent A2A Server"""
import os
import sys
import asyncio
import logging
import click
import uvicorn
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agents.a2a_agents.legal_researcher.executor import LegalResearcherExecutor
from agents.a2a_agents.legal_researcher.agent import LegalResearcherAgent

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 10002


def get_agent_card(host: str, port: int) -> AgentCard:
    capabilities = AgentCapabilities(streaming=True, push_notifications=False)
    skills = [
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
    ]
    app_url = os.environ.get('APP_URL', f'http://{host}:{port}')
    return AgentCard(
        name='Legal Researcher Agent',
        description='Finds supporting verdicts, citations, and novel legal theories to strengthen cases',
        url=app_url,
        version='1.0.0',
        default_input_modes=LegalResearcherAgent.SUPPORTED_CONTENT_TYPES,
        default_output_modes=LegalResearcherAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=skills,
    )


def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, log_level: str = 'info'):
    if not os.getenv('GEMINI_API_KEY'):
        raise ValueError('GEMINI_API_KEY environment variable not set')
    
    async def run_server_async():
        logger.info('Initializing Legal Researcher Agent server...')
        executor = LegalResearcherExecutor()
        request_handler = DefaultRequestHandler(agent_executor=executor, task_store=InMemoryTaskStore())
        a2a_server = A2AStarletteApplication(agent_card=get_agent_card(host, port), http_handler=request_handler)
        asgi_app = a2a_server.build()
        config = uvicorn.Config(app=asgi_app, host=host, port=port, log_level=log_level.lower())
        uvicorn_server = uvicorn.Server(config)
        logger.info(f'Starting Legal Researcher Agent server at http://{host}:{port}')
        try:
            await uvicorn_server.serve()
        except KeyboardInterrupt:
            logger.info('Server shutdown requested.')
    
    try:
        asyncio.run(run_server_async())
    except Exception as e:
        logger.error(f'Error: {e}', exc_info=True)
        sys.exit(1)


@click.command()
@click.option('--host', default=DEFAULT_HOST)
@click.option('--port', default=DEFAULT_PORT, type=int)
@click.option('--log-level', default='info')
def cli(host: str, port: int, log_level: str):
    main(host, port, log_level)


if __name__ == '__main__':
    cli()

