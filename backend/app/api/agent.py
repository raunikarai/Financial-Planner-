"""Agent API endpoints for the Financial Planner chatbot."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.financial_agent import FinancialPlannerAgent

router = APIRouter(prefix="/agent", tags=["agent"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    reply: str


# Initialize the agent
agent = FinancialPlannerAgent()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat with the Financial Planner Agent.
    
    Args:
        request: ChatRequest containing the user's message
        
    Returns:
        ChatResponse with the agent's reply
    """
    reply = agent.respond(request.message)
    return ChatResponse(reply=reply)
