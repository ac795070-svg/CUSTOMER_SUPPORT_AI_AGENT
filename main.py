import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

customer_support_agent = Agent(
    name="customer_support_agent",
    model="gemini-3.6-flash",
    instruction="""You are a friendly customer support agent for an online store.
    Help customers with questions about orders, returns, refunds, and product info.
    Be polite, clear, and concise. If unsure, say you'll escalate to a human agent.""",
    description="AI customer support agent"
)

APP_NAME = "customer_support_app"
USER_ID = "test_user"

async def main():
    runner = InMemoryRunner(agent=customer_support_agent, app_name=APP_NAME)
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    print("Customer Support Agent Ready! (type 'exit' to quit)")
    while True:
        query = input("You: ")
        if query.lower() == "exit":
            break
        user_message = types.Content(role="user", parts=[types.Part(text=query)])
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=user_message
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print("Agent:", event.content.parts[0].text)

if __name__ == "__main__":
    asyncio.run(main())