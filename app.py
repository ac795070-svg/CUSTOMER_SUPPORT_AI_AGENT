import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

customer_support_agent = Agent(
    name="customer_support_agent",
    model="gemini-3.6-flash",
    instruction="""You are a friendly customer support agent for an online store.
    Help customers with questions about orders, returns, refunds, and product info.
    Be polite, clear, and concise. If unsure, say you'll escalate to a human agent.""",
    description="AI customer support agent"
)

APP_NAME = "customer_support_app"
runner = InMemoryRunner(agent=customer_support_agent, app_name=APP_NAME)

class ChatRequest(BaseModel):
    message: str
    user_id: str = "web_user"
    session_id: str = "default_session"

@app.get("/")
def home():
    return FileResponse("index.html")

@app.post("/chat")
async def chat(req: ChatRequest):
    session = await runner.session_service.get_session(
    app_name=APP_NAME, user_id=req.user_id, session_id=req.session_id
    )
    if session is None:
        session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=req.user_id, session_id=req.session_id
    )

    user_message = types.Content(role="user", parts=[types.Part(text=req.message)])
    reply = ""
    async for event in runner.run_async(
        user_id=req.user_id,
        session_id=session.id,
        new_message=user_message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            reply = event.content.parts[0].text

    return {"reply": reply}