"""Agent API endpoints for the Financial Planner chatbot."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.agents.financial_agent import FinancialPlannerAgent
from app.api.dependencies import get_current_user
from app.models.user import User

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
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
) -> ChatResponse:
    """
    Chat with the Financial Planner Agent.
    
    Requires authentication via JWT token.
    
    Args:
        request: ChatRequest containing the user's message
        current_user: Authenticated user from JWT token
        
    Returns:
        ChatResponse with the agent's reply
    """
    reply = agent.respond(request.message, user_id=current_user.user_id)
    return ChatResponse(reply=reply)
