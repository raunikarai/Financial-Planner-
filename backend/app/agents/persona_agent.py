"""Persona Agent - Handles all persona-related logic."""

from typing import Optional

from app.memory.persona_store import (
    get_persona as _get_persona,
    set_income as _set_income,
    set_risk_level as _set_risk_level,
    set_primary_goal as _set_primary_goal,
    get_missing_fields as _get_missing_fields,
    clear_persona as _clear_persona
)


class PersonaAgent:
    """
    Agent responsible for managing user persona data.
    
    This agent owns all persona-related logic and provides a clean interface
    for other agents to access persona information without directly touching
    the persona store.
    """

    def get_persona(self, user_id: str = "default") -> dict:
        """
        Get the persona for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Dictionary with persona data:
            - monthly_income: float or None
            - risk_level: str or None ("low", "medium", "high")
            - primary_goal: str or None
        """
        persona = _get_persona(user_id)
        return {
            "monthly_income": persona.monthly_income,
            "risk_level": persona.risk_level,
            "primary_goal": persona.primary_goal
        }

    def update_persona(self, user_id: str, data: dict) -> dict:
        """
        Update persona fields for a user.
        
        Args:
            user_id: The user identifier
            data: Dictionary with fields to update. Supported keys:
                  - monthly_income: float
                  - risk_level: str ("low", "medium", "high")
                  - primary_goal: str
                  
        Returns:
            Updated persona dictionary
        """
        if "monthly_income" in data and data["monthly_income"] is not None:
            _set_income(data["monthly_income"], user_id)
        
        if "risk_level" in data and data["risk_level"] is not None:
            _set_risk_level(data["risk_level"], user_id)
        
        if "primary_goal" in data and data["primary_goal"] is not None:
            _set_primary_goal(data["primary_goal"], user_id)
        
        return self.get_persona(user_id)

    def get_missing_fields(self, user_id: str = "default") -> list[str]:
        """
        Get list of persona fields that haven't been set yet.
        
        Args:
            user_id: The user identifier
            
        Returns:
            List of missing field names
        """
        return _get_missing_fields(user_id)

    def clear_persona(self, user_id: str = "default") -> None:
        """
        Clear persona data for a user (useful for testing).
        
        Args:
            user_id: The user identifier
        """
        _clear_persona(user_id)

    def has_income(self, user_id: str = "default") -> bool:
        """Check if user has set their income."""
        persona = self.get_persona(user_id)
        return persona["monthly_income"] is not None

    def has_risk_level(self, user_id: str = "default") -> bool:
        """Check if user has set their risk level."""
        persona = self.get_persona(user_id)
        return persona["risk_level"] is not None

    def has_primary_goal(self, user_id: str = "default") -> bool:
        """Check if user has set their primary goal."""
        persona = self.get_persona(user_id)
        return persona["primary_goal"] is not None


# Singleton instance
_persona_agent: Optional[PersonaAgent] = None


def get_persona_agent() -> PersonaAgent:
    """Get or create the PersonaAgent singleton."""
    global _persona_agent
    if _persona_agent is None:
        _persona_agent = PersonaAgent()
    return _persona_agent
