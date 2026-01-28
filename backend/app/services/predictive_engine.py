"""Predictive Engine for cashflow forecasting - deterministic, no ML."""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.tools.expense_tools import get_all_expenses
from app.memory.persona_store import get_persona


@dataclass
class CashflowPrediction:
    """Cashflow prediction result."""
    daily_income: float
    total_expenses: float
    expense_count: int
    avg_daily_expense: float
    daily_burn_rate: float  # Positive = spending more than earning
    days_to_zero: Optional[int]  # None if not burning cash
    risk_level: str  # "low", "medium", "high"
    monthly_income: Optional[float]
    

def calculate_avg_daily_expense(expenses: list[dict], days: int = 30) -> tuple[float, float, int]:
    """
    Calculate average daily expense from stored expenses.
    
    Args:
        expenses: List of expense records
        days: Number of days to consider (default 30)
        
    Returns:
        Tuple of (avg_daily_expense, total_expenses, expense_count)
    """
    if not expenses:
        return 0.0, 0.0, 0
    
    # Get expenses from the last N days
    cutoff_date = datetime.now() - timedelta(days=days)
    
    recent_expenses = []
    for exp in expenses:
        # Parse the created_at timestamp
        try:
            exp_date = datetime.fromisoformat(exp.get("created_at", ""))
            if exp_date >= cutoff_date:
                recent_expenses.append(exp)
        except (ValueError, TypeError):
            # If date parsing fails, include the expense
            recent_expenses.append(exp)
    
    if not recent_expenses:
        # Use all expenses if no recent ones
        recent_expenses = expenses
    
    total = sum(exp.get("amount", 0) for exp in recent_expenses)
    count = len(recent_expenses)
    
    # Calculate average daily expense
    # If we have expenses, assume they span the analysis period
    avg_daily = total / days if total > 0 else 0.0
    
    return avg_daily, total, count


def predict_cashflow(user_id: str = "default") -> dict:
    """
    Predict cashflow based on current spending patterns.
    
    Args:
        user_id: The user identifier
        
    Returns:
        Dictionary with prediction data:
        - daily_income: float
        - total_expenses: float
        - expense_count: int
        - avg_daily_expense: float
        - daily_burn_rate: float (positive = spending more than earning)
        - days_remaining_in_month: int
        - projected_shortfall: float (how much over budget by month end)
        - risk_level: "low", "medium", or "high"
        - monthly_income: float or None
    """
    # Get user persona
    persona = get_persona(user_id)
    monthly_income = persona.monthly_income or 0.0
    
    # Calculate daily income
    daily_income = monthly_income / 30
    
    # Get expenses and calculate average
    expenses = get_all_expenses(user_id)
    avg_daily_expense, total_expenses, expense_count = calculate_avg_daily_expense(expenses)
    
    # Calculate daily burn rate (positive = losing money)
    daily_burn_rate = avg_daily_expense - daily_income
    
    # Calculate remaining days in month
    today = datetime.now()
    days_in_month = 30  # Simplified
    current_day = today.day
    days_remaining = max(days_in_month - current_day, 1)
    
    # Determine risk level based on projected spending
    risk_level: str = "low"
    projected_shortfall: float = 0.0
    
    if daily_burn_rate <= 0:
        # Not burning cash - income exceeds or equals expenses
        risk_level = "low"
        projected_shortfall = 0.0
    else:
        # Calculate projected shortfall by end of month
        # Shortfall = overspending per day × remaining days
        projected_shortfall = daily_burn_rate * days_remaining
        
        # Determine risk level based on shortfall percentage of income
        if monthly_income > 0:
            shortfall_percentage = (projected_shortfall / monthly_income) * 100
            
            if shortfall_percentage >= 30:
                risk_level = "high"
            elif shortfall_percentage >= 15:
                risk_level = "medium"
            else:
                risk_level = "low"
        else:
            risk_level = "high" if projected_shortfall > 0 else "low"
    
    return {
        "daily_income": round(daily_income, 2),
        "total_expenses": round(total_expenses, 2),
        "expense_count": expense_count,
        "avg_daily_expense": round(avg_daily_expense, 2),
        "daily_burn_rate": round(daily_burn_rate, 2),
        "days_remaining_in_month": days_remaining,
        "projected_shortfall": round(projected_shortfall, 2),
        "risk_level": risk_level,
        "monthly_income": monthly_income
    }


def format_prediction_insight(prediction: dict) -> str:
    """
    Convert prediction data into a human-readable insight.
    
    Args:
        prediction: Prediction dictionary from predict_cashflow
        
    Returns:
        Human-readable insight string
    """
    if prediction["expense_count"] == 0:
        return "I don't have enough expense data yet to predict your cashflow. Try logging a few expenses first!"
    
    if prediction["monthly_income"] is None or prediction["monthly_income"] == 0:
        return (
            f"Based on {prediction['expense_count']} expenses totaling ₹{prediction['total_expenses']:,.0f}, "
            f"your average daily spending is ₹{prediction['avg_daily_expense']:,.0f}. "
            "Set your monthly income so I can give you better predictions!"
        )
    
    insight_parts = []
    days_remaining = prediction["days_remaining_in_month"]
    
    # Daily comparison
    insight_parts.append(
        f"📊 **Cashflow Analysis** ({days_remaining} days left in month)\n"
        f"• Daily income: ₹{prediction['daily_income']:,.0f}\n"
        f"• Avg daily spending: ₹{prediction['avg_daily_expense']:,.0f}"
    )
    
    # Risk assessment
    if prediction["daily_burn_rate"] <= 0:
        savings_rate = abs(prediction["daily_burn_rate"])
        monthly_savings = savings_rate * 30
        insight_parts.append(
            f"\n\n✅ **Great news!** You're saving ₹{savings_rate:,.0f} per day on average.\n"
            f"At this rate, you could save ~₹{monthly_savings:,.0f} this month. Keep it up!"
        )
    else:
        shortfall = prediction["projected_shortfall"]
        risk = prediction["risk_level"]
        
        if risk == "high":
            emoji = "🚨"
            urgency = "Strongly consider cutting back on non-essential spending!"
        elif risk == "medium":
            emoji = "⚠️"
            urgency = "Consider reducing spending to stay on track."
        else:
            emoji = "ℹ️"
            urgency = "You have some buffer, but keep an eye on it."
        
        insight_parts.append(
            f"\n\n{emoji} **Alert:** You're spending ₹{prediction['daily_burn_rate']:,.0f} more than you earn daily.\n"
            f"With **{days_remaining} days** left, you may overspend by **₹{shortfall:,.0f}** this month.\n"
            f"{urgency}"
        )
    
    return "".join(insight_parts)
