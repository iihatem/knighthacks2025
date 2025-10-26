import asyncio

from agents.orchistrator_agent.agent import orchistrator_agent
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import inMemorySessionService

load_dotenv()

session_service = inMemorySessionService()

initial_state = {
    "user_name": "John Doe",

}

async def main_async():

APP_NAME = "TenderPilot"
USER_ID = "Johnny"

#create a session

new_session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    state=initial_state
)

#create a runner

runner = Runner(
    app=app,
    session_service=session_service
)

SESSION_ID = new_session.id
print(f"Session created with ID: {SESSION_ID}")


# Interactive convo loop

print("\nWelcome to the TenderPilot!")
print("Type 'exit' to end the conversation.")

while True:
    user_input = input("[user]: ")
    if user_input.lower() == "exit":
        break
    else:
        async with Aclosing(
            runner.run_async(
                user_id=USER_ID,
                session_id=SESSION_ID,
                new_message=user_input
            )
        ) as agen: