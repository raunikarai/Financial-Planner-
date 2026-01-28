"""Expense tools for the Financial Planner Agent.

This module provides a facade over the expense repository,
maintaining the same interface for backward compatibility.
"""

from typing import Optional

from app.repositories import expense_repo


# Default user ID for backward compatibility
DEFAULT_USER_ID = "default"


def add_expense(
    amount: float, 
    category: str, 
    note: Optional[str] = None,
    user_id: str = DEFAULT_USER_ID
) -> dict:
    """
    Add an expense to the database.
    
    Args:
        amount: The expense amount
        category: The expense category (e.g., food, rent, transport)
        note: Optional note/description for the expense
        user_id: The user identifier (defaults to "default")
        
    Returns:
        The created expense record
    """
    return expense_repo.add_expense(
        user_id=user_id,
        amount=amount,
        category=category,
        note=note
    )


def get_all_expenses(user_id: str = DEFAULT_USER_ID) -> list[dict]:
    """
    Return all stored expenses for a user.
    
    Args:
        user_id: The user identifier (defaults to "default")
        
    Returns:
        List of expense dictionaries
    """
    return expense_repo.get_expenses(user_id)


def clear_expenses(user_id: str = DEFAULT_USER_ID) -> None:
    """
    Clear all expenses for a user (useful for testing).
    
    Args:
        user_id: The user identifier (defaults to "default")
    """
    expense_repo.clear_expenses(user_id)
