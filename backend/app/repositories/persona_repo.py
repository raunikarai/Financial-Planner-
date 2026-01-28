"""Persona repository - handles all persona-related database operations."""

from typing import Optional

from app.db.session import get_session
from app.models.user import User
from app.models.persona import Persona


def get_or_create_user(user_id: str) -> dict:
    """
    Get a user by ID, creating if it doesn't exist.
    
    Args:
        user_id: The user identifier
        
    Returns:
        User dictionary
    """
    session = get_session()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            user = User(user_id=user_id)
            session.add(user)
            session.commit()
            session.refresh(user)
        
        return {"user_id": user.user_id, "created_at": user.created_at.isoformat()}
    finally:
        session.close()


def get_persona(user_id: str) -> dict:
    """
    Get persona for a user.
    
    Args:
        user_id: The user identifier
        
    Returns:
        Persona dictionary with monthly_income, risk_level, primary_goal
    """
    session = get_session()
    try:
        # Ensure user exists
        get_or_create_user(user_id)
        
        persona = session.query(Persona).filter(Persona.user_id == user_id).first()
        
        if persona:
            return persona.to_dict()
        
        # Return default empty persona
        return {
            "user_id": user_id,
            "monthly_income": None,
            "risk_level": None,
            "primary_goal": None
        }
    finally:
        session.close()


def upsert_persona(user_id: str, data: dict) -> dict:
    """
    Create or update persona for a user.
    
    Args:
        user_id: The user identifier
        data: Dict with fields to update (monthly_income, risk_level, primary_goal)
        
    Returns:
        Updated persona dictionary
    """
    session = get_session()
    try:
        # Ensure user exists
        get_or_create_user(user_id)
        
        persona = session.query(Persona).filter(Persona.user_id == user_id).first()
        
        if not persona:
            # Create new persona
            persona = Persona(user_id=user_id)
            session.add(persona)
        
        # Update fields if provided
        if "monthly_income" in data:
            persona.monthly_income = data["monthly_income"]
        if "risk_level" in data:
            persona.risk_level = data["risk_level"]
        if "primary_goal" in data:
            persona.primary_goal = data["primary_goal"]
        
        session.commit()
        session.refresh(persona)
        
        return persona.to_dict()
    finally:
        session.close()


def delete_persona(user_id: str) -> bool:
    """
    Delete persona for a user.
    
    Args:
        user_id: The user identifier
        
    Returns:
        True if deleted, False if not found
    """
    session = get_session()
    try:
        count = session.query(Persona).filter(Persona.user_id == user_id).delete()
        session.commit()
        return count > 0
    finally:
        session.close()
