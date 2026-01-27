"""Expense tools for the Financial Planner Agent."""

from typing import Optional
from datetime import datetime

# In-memory storage for expenses
expenses: list[dict] = []


def add_expense(amount: float, category: str, note: Optional[str] = None) -> dict:
    """
    Add an expense to the in-memory store.
    
    Args:
        amount: The expense amount
        category: The expense category (e.g., food, rent, transport)
        note: Optional note/description for the expense
        
    Returns:
        The created expense record
    """
    expense = {
        "id": len(expenses) + 1,
        "amount": amount,
        "category": category.lower(),
        "note": note,
        "created_at": datetime.now().isoformat()
    }
    expenses.append(expense)
    return expense


def get_all_expenses() -> list[dict]:
    """Return all stored expenses."""
    return expenses


def clear_expenses() -> None:
    """Clear all expenses (useful for testing)."""
    expenses.clear()
