"""Database session configuration for SQLite."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Database file location - in the backend directory
DB_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(DB_DIR, "financial_planner.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine with SQLite-specific settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite with FastAPI
    echo=False  # Set to True to see SQL queries in console
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session() -> Session:
    """
    Get a new database session directly.
    
    Use this in non-FastAPI contexts (like repositories).
    Remember to close the session when done.
    """
    return SessionLocal()


def init_db():
    """
    Initialize the database by creating all tables.
    
    Call this at application startup.
    """
    from app.db.base import Base
    # Import all models to register them with Base.metadata
    from app.models import user, expense, persona, budget  # noqa: F401
    
    Base.metadata.create_all(bind=engine)
    print(f"[DB] Database initialized at: {DB_PATH}")
