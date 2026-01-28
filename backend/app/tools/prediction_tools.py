"""Prediction tools for the Financial Planner Agent."""

from app.services.predictive_engine import predict_cashflow as _predict_cashflow


def predict_cashflow(user_id: str = "default") -> dict:
    """
    Predict cashflow based on current spending patterns.
    
    This is a tool wrapper for the predictive engine.
    
    Args:
        user_id: The user identifier
        
    Returns:
        Dictionary with numeric prediction data:
        - daily_income: float
        - total_expenses: float
        - expense_count: int
        - avg_daily_expense: float
        - daily_burn_rate: float (positive = spending more than earning)
        - days_to_zero: int or None
        - risk_level: "low", "medium", or "high"
        - monthly_income: float or None
    """
    return _predict_cashflow(user_id)
