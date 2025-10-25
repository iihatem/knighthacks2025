from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="basic_agent",
    model="gemini-2.5-flash",
    description="A basic agent that can answer questions and perform tasks",
    tools=[google_search],
)