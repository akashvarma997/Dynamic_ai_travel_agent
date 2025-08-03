# main.py

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import the factory function from the 'agent' package
from agent.factory import get_session_agent

# Load environment variables from .env file
load_dotenv()

# Ensure API keys are set
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable not set.")
if not os.getenv("TAVILY_API_KEY"):
    raise ValueError("TAVILY_API_KEY environment variable not set.")

# Create the FastAPI app
app = FastAPI(
    title="Dynamic AI Travel Agent",
    description="A conversational AI agent for travel planning using FastAPI and LangChain.",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic models for the request and response body
class ChatRequest(BaseModel):
    query: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Handles chat interactions with the AI Travel Agent."""
    executor = get_session_agent(request.session_id)
    response = await executor.ainvoke({"input": request.query})
    return ChatResponse(response=response["output"], session_id=request.session_id)