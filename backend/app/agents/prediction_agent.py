"""Prediction Agent - Handles all predictive/forecasting logic."""

from typing import Optional

from app.services.predictive_engine import predict_cashflow as _predict_cashflow


class PredictionAgent:
    """
    Agent responsible for financial predictions and risk assessment.
    
    This agent owns all prediction logic and provides a clean interface
    for other agents to access forecasts without directly touching
    the predictive engine.
    """

    def predict_financial_risk(self, user_id: str = "default") -> dict:
        """
        Predict financial risk based on current spending patterns.
        
        This method returns numeric prediction results only - no natural
        language generation. The orchestrating agent is responsible for
        converting these numbers into user-friendly messages.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Dictionary with numeric prediction data:
            - daily_income: float
            - total_expenses: float
            - expense_count: int
            - avg_daily_expense: float
            - daily_burn_rate: float (positive = spending more than earning)
            - days_remaining_in_month: int
            - projected_shortfall: float
            - risk_level: "low", "medium", or "high"
            - monthly_income: float or None
        """
        return _predict_cashflow(user_id)

    def can_afford(self, amount: float, user_id: str = "default") -> dict:
        """
        Check if user can afford a specific purchase.
        
        Args:
            amount: The amount to check
            user_id: The user identifier
            
        Returns:
            Dictionary with affordability analysis:
            - can_afford: bool
            - daily_savings: float (negative if overspending)
            - days_to_save: int or None (if saving)
            - risk_level: str
            - recommendation: "yes", "caution", or "no"
        """
        prediction = self.predict_financial_risk(user_id)
        
        daily_burn_rate = prediction["daily_burn_rate"]
        
        if daily_burn_rate <= 0:
            # User is saving money
            daily_savings = abs(daily_burn_rate)
            days_to_save = int(amount / daily_savings) if daily_savings > 0 else None
            
            if days_to_save is not None and days_to_save <= 7:
                recommendation = "yes"
                can_afford = True
            elif days_to_save is not None and days_to_save <= 30:
                recommendation = "caution"
                can_afford = True
            else:
                recommendation = "caution"
                can_afford = False
        else:
            # User is overspending
            daily_savings = -daily_burn_rate
            days_to_save = None
            recommendation = "no"
            can_afford = False
        
        return {
            "can_afford": can_afford,
            "daily_savings": round(daily_savings, 2),
            "days_to_save": days_to_save,
            "risk_level": prediction["risk_level"],
            "recommendation": recommendation,
            "daily_burn_rate": round(daily_burn_rate, 2),
            "monthly_income": prediction["monthly_income"],
            "expense_count": prediction["expense_count"]
        }

    def get_risk_summary(self, user_id: str = "default") -> dict:
        """
        Get a summary of user's financial risk status.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Dictionary with risk summary:
            - risk_level: str
            - is_overspending: bool
            - projected_shortfall: float
            - days_remaining: int
        """
        prediction = self.predict_financial_risk(user_id)
        
        return {
            "risk_level": prediction["risk_level"],
            "is_overspending": prediction["daily_burn_rate"] > 0,
            "projected_shortfall": prediction["projected_shortfall"],
            "days_remaining": prediction["days_remaining_in_month"]
        }


# Singleton instance
_prediction_agent: Optional[PredictionAgent] = None


def get_prediction_agent() -> PredictionAgent:
    """Get or create the PredictionAgent singleton."""
    global _prediction_agent
    if _prediction_agent is None:
        _prediction_agent = PredictionAgent()
    return _prediction_agent
