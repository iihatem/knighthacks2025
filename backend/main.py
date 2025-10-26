import asyncio

from agents.orchistrator_agent.agent import orchistrator_agent
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import inMemorySessionService

load_dotenv()