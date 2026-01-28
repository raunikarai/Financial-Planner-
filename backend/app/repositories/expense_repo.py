"""Expense repository - handles all expense-related database operations."""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import func

from app.db.session import get_session
from app.models.expense import Expense
from app.repositories.persona_repo import get_or_create_user


def add_expense(
    user_id: str, 
    amount: float, 
    category: str, 
    note: Optional[str] = None
) -> dict:
    """
    Add an expense to the database.
    
    Args:
        user_id: The user identifier
        amount: The expense amount
        category: The expense category
        note: Optional note/description
        
    Returns:
        The created expense as a dictionary
    """
    session = get_session()
    try:
        # Ensure user exists
        get_or_create_user(user_id)
        
        expense = Expense(
            user_id=user_id,
            amount=amount,
            category=category.lower(),
            note=note,
            created_at=datetime.utcnow()
        )
        session.add(expense)
        session.commit()
        session.refresh(expense)
        
        return expense.to_dict()
    finally:
        session.close()


def get_expenses(user_id: str) -> List[dict]:
    """
    Get all expenses for a user.
    
    Args:
        user_id: The user identifier
        
    Returns:
        List of expense dictionaries
    """
    session = get_session()
    try:
        expenses = session.query(Expense).filter(
            Expense.user_id == user_id
        ).order_by(Expense.created_at.desc()).all()
        
        return [exp.to_dict() for exp in expenses]
    finally:
        session.close()


def get_expenses_by_category(user_id: str, category: str) -> List[dict]:
    """
    Get expenses for a specific category.
    
    Args:
        user_id: The user identifier
        category: The expense category
        
    Returns:
        List of expense dictionaries
    """
    session = get_session()
    try:
        expenses = session.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.category == category.lower()
        ).order_by(Expense.created_at.desc()).all()
        
        return [exp.to_dict() for exp in expenses]
    finally:
        session.close()


def get_total_spending(user_id: str, category: Optional[str] = None) -> float:
    """
    Get total spending, optionally filtered by category.
    
    Args:
        user_id: The user identifier
        category: Optional category filter
        
    Returns:
        Total spending amount
    """
    session = get_session()
    try:
        query = session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id
        )
        
        if category:
            query = query.filter(Expense.category == category.lower())
        
        result = query.scalar()
        return result or 0.0
    finally:
        session.close()


def get_category_spending_summary(user_id: str) -> dict:
    """
    Get spending summary grouped by category.
    
    Args:
        user_id: The user identifier
        
    Returns:
        Dict mapping category to total spending
    """
    session = get_session()
    try:
        results = session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id
        ).group_by(Expense.category).all()
        
        return {row.category: row.total for row in results}
    finally:
        session.close()


def get_expense_count(user_id: str) -> int:
    """
    Get the number of expenses for a user.
    
    Args:
        user_id: The user identifier
        
    Returns:
        Number of expenses
    """
    session = get_session()
    try:
        return session.query(Expense).filter(
            Expense.user_id == user_id
        ).count()
    finally:
        session.close()


def clear_expenses(user_id: str) -> int:
    """
    Delete all expenses for a user (useful for testing).
    
    Args:
        user_id: The user identifier
        
    Returns:
        Number of expenses deleted
    """
    session = get_session()
    try:
        count = session.query(Expense).filter(
            Expense.user_id == user_id
        ).delete()
        session.commit()
        return count
    finally:
        session.close()
