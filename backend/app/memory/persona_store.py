"""Persona store for user financial profile memory.

This module provides a facade over the persona repository,
maintaining the same interface for backward compatibility.
"""

from typing import Optional
from dataclasses import dataclass

from app.repositories import persona_repo


@dataclass
class Persona:
    """User persona containing financial profile information."""
    monthly_income: Optional[float] = None
    risk_level: Optional[str] = None  # "low", "medium", "high"
    primary_goal: Optional[str] = None  # e.g., "savings", "investment", "debt_repayment"


def get_persona(user_id: str = "default") -> Persona:
    """
    Get persona for a user from database.
    
    Args:
        user_id: The user identifier
        
    Returns:
        The user's persona as a Persona dataclass
    """
    data = persona_repo.get_persona(user_id)
    return Persona(
        monthly_income=data.get("monthly_income"),
        risk_level=data.get("risk_level"),
        primary_goal=data.get("primary_goal")
    )


def set_income(income: float, user_id: str = "default") -> Persona:
    """Set user's monthly income."""
    persona_repo.upsert_persona(user_id, {"monthly_income": income})
    return get_persona(user_id)


def set_risk_level(risk_level: str, user_id: str = "default") -> Persona:
    """Set user's risk tolerance level."""
    persona_repo.upsert_persona(user_id, {"risk_level": risk_level.lower()})
    return get_persona(user_id)


def set_primary_goal(goal: str, user_id: str = "default") -> Persona:
    """Set user's primary financial goal."""
    persona_repo.upsert_persona(user_id, {"primary_goal": goal.lower()})
    return get_persona(user_id)


def clear_persona(user_id: str = "default") -> None:
    """Clear persona data for a user (useful for testing)."""
    persona_repo.delete_persona(user_id)


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
