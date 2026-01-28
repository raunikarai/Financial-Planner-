"""Budget model for the Financial Planner application."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Budget(Base):
    """Budget model - stores budget limits per category."""
    
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("users.user_id"), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # 'total' for overall budget
    limit_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="budgets")
    
    # Unique constraint on user_id + category
    __table_args__ = (
        # Each user can have only one budget per category
        {"sqlite_autoincrement": True},
    )
    
    def to_dict(self) -> dict:
        """Convert budget to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category": self.category,
            "limit_amount": self.limit_amount
        }
    
    def __repr__(self):
        return f"<Budget(user_id='{self.user_id}', category='{self.category}', limit={self.limit_amount})>"
