"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agent import router as agent_router
from app.db.session import init_db

app = FastAPI(
    title="Financial Planner API",
    description="AI-powered personal finance planning assistant",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Initialize database tables on application startup."""
    init_db()

# Include routers
app.include_router(agent_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Financial Planner API is running"}
