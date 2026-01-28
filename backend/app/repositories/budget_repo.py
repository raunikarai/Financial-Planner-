"""Budget repository - handles all budget-related database operations."""

from typing import Optional, List

from app.db.session import get_session
from app.models.budget import Budget
from app.repositories.persona_repo import get_or_create_user


def get_budgets(user_id: str) -> dict:
    """
    Get all budget limits for a user.
    
    Args:
        user_id: The user identifier
        
    Returns:
        Dict with category_limits and total_limit
    """
    session = get_session()
    try:
        budgets = session.query(Budget).filter(Budget.user_id == user_id).all()
        
        category_limits = {}
        total_limit = None
        
        for budget in budgets:
            if budget.category == "total":
                total_limit = budget.limit_amount
            else:
                category_limits[budget.category] = budget.limit_amount
        
        return {
            "category_limits": category_limits,
            "total_limit": total_limit
        }
    finally:
        session.close()


def get_budget_by_category(user_id: str, category: str) -> Optional[float]:
    """
    Get budget limit for a specific category.
    
    Args:
        user_id: The user identifier
        category: The budget category
        
    Returns:
        Budget limit amount or None if not set
    """
    session = get_session()
    try:
        budget = session.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.category == category.lower()
        ).first()
        
        return budget.limit_amount if budget else None
    finally:
        session.close()


def upsert_budget(user_id: str, category: str, limit_amount: float) -> dict:
    """
    Create or update a budget limit.
    
    Args:
        user_id: The user identifier
        category: The budget category (or 'total' for overall budget)
        limit_amount: The budget limit
        
    Returns:
        Budget dictionary
    """
    session = get_session()
    try:
        # Ensure user exists
        get_or_create_user(user_id)
        
        category = category.lower()
        budget = session.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.category == category
        ).first()
        
        if budget:
            budget.limit_amount = limit_amount
        else:
            budget = Budget(
                user_id=user_id,
                category=category,
                limit_amount=limit_amount
            )
            session.add(budget)
        
        session.commit()
        session.refresh(budget)
        
        return budget.to_dict()
    finally:
        session.close()


def delete_budget(user_id: str, category: str) -> bool:
    """
    Delete a budget limit.
    
    Args:
        user_id: The user identifier
        category: The budget category
        
    Returns:
        True if deleted, False if not found
    """
    session = get_session()
    try:
        count = session.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.category == category.lower()
        ).delete()
        session.commit()
        return count > 0
    finally:
        session.close()


def get_all_budget_categories(user_id: str) -> List[str]:
    """
    Get all categories with budget limits.
    
    Args:
        user_id: The user identifier
        
    Returns:
        List of category names
    """
    session = get_session()
    try:
        budgets = session.query(Budget.category).filter(
            Budget.user_id == user_id
        ).all()
        
        return [b.category for b in budgets if b.category != "total"]
    finally:
        session.close()
