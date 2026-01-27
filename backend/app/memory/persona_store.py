"""Persona store for user financial profile memory."""

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Persona:
    """User persona containing financial profile information."""
    monthly_income: Optional[float] = None
    risk_level: Optional[str] = None  # "low", "medium", "high"
    primary_goal: Optional[str] = None  # e.g., "savings", "investment", "debt_repayment"


# In-memory persona storage (keyed by user_id)
_persona_store: dict[str, Persona] = {}


def get_persona(user_id: str = "default") -> Persona:
    """
    Get persona for a user, creating empty one if not exists.
    
    Args:
        user_id: The user identifier
        
    Returns:
        The user's persona
    """
    if user_id not in _persona_store:
        _persona_store[user_id] = Persona()
    return _persona_store[user_id]


def set_income(income: float, user_id: str = "default") -> Persona:
    """Set user's monthly income."""
    persona = get_persona(user_id)
    persona.monthly_income = income
    return persona


def set_risk_level(risk_level: str, user_id: str = "default") -> Persona:
    """Set user's risk tolerance level."""
    persona = get_persona(user_id)
    persona.risk_level = risk_level.lower()
    return persona


def set_primary_goal(goal: str, user_id: str = "default") -> Persona:
    """Set user's primary financial goal."""
    persona = get_persona(user_id)
    persona.primary_goal = goal.lower()
    return persona


def clear_persona(user_id: str = "default") -> None:
    """Clear persona data for a user (useful for testing)."""
    if user_id in _persona_store:
        del _persona_store[user_id]


def get_missing_fields(user_id: str = "default") -> list[str]:
    """Get list of persona fields that haven't been set yet."""
    persona = get_persona(user_id)
    missing = []
    if persona.monthly_income is None:
        missing.append("monthly_income")
    if persona.risk_level is None:
        missing.append("risk_level")
    if persona.primary_goal is None:
        missing.append("primary_goal")
    return missing
