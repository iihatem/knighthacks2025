from google.adk.agents import Agent
from google.adk.tools import google_search

#can only use one built in tool at a time

### add your own python function
def get_current_weather(city: dict) -> dict:
    """Get the current weather for a given city"""
    return {
        
        "weather": f"The weather in {city} is sunny"

    }

root_agent = Agent(
    name="tool_agent",
    model="gemini-2.5-flash",
    description="tool agent that can use tools to perform tasks",
    tools=[google_search],
)