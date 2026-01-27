"""Main FastAPI application entry point."""

from fastapi import FastAPI

from app.api.agent import router as agent_router

app = FastAPI(
    title="Financial Planner API",
    description="AI-powered personal finance planning assistant",
    version="1.0.0"
)

# Include routers
app.include_router(agent_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Financial Planner API is running"}
