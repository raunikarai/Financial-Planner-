"""Persona model for the Financial Planner application."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Persona(Base):
    """Persona model - stores user profile and preferences."""
    
    __tablename__ = "personas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    monthly_income = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)  # low, medium, high
    primary_goal = Column(String(50), nullable=True)  # savings, investment, debt_repayment, retirement, education
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="persona")
    
    def to_dict(self) -> dict:
        """Convert persona to dictionary."""
        return {
            "user_id": self.user_id,
            "monthly_income": self.monthly_income,
            "risk_level": self.risk_level,
            "primary_goal": self.primary_goal
        }
    
    def __repr__(self):
        return f"<Persona(user_id='{self.user_id}', income={self.monthly_income}, risk='{self.risk_level}')>"
