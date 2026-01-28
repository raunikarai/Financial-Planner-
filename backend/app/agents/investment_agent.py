"""Investment Strategy Agent for the A2A architecture.

Provides high-level investment allocation strategies based on user persona.
All logic is deterministic and explainable - no ML or market data.
"""

from typing import Optional

from app.agents.persona_agent import get_persona_agent
from app.agents.prediction_agent import get_prediction_agent
from app.repositories import expense_repo


class InvestmentStrategyAgent:
    """
    Agent responsible for investment allocation strategy recommendations.
    
    This agent:
    - Analyzes user persona (income, risk level, goals)
    - Considers current financial health (emergency fund status)
    - Outputs deterministic allocation percentages
    - Does NOT recommend specific products or instruments
    
    All logic is deterministic and explainable.
    """

    # Allocation templates based on risk profile
    ALLOCATION_TEMPLATES = {
        "conservative": {
            "equity": 20,
            "debt": 50,
            "emergency_fund": 30
        },
        "balanced": {
            "equity": 40,
            "debt": 40,
            "emergency_fund": 20
        },
        "aggressive": {
            "equity": 60,
            "debt": 25,
            "emergency_fund": 15
        }
    }

    # Goal-based adjustments
    GOAL_ADJUSTMENTS = {
        "savings": {"equity": -10, "debt": 0, "emergency_fund": 10},
        "investment": {"equity": 10, "debt": 0, "emergency_fund": -10},
        "debt_repayment": {"equity": -15, "debt": 15, "emergency_fund": 0},
        "retirement": {"equity": 5, "debt": 5, "emergency_fund": -10},
        "education": {"equity": 0, "debt": 10, "emergency_fund": -10},
    }

    def __init__(self):
        """Initialize the InvestmentStrategyAgent."""
        self._persona_agent = get_persona_agent()
        self._prediction_agent = get_prediction_agent()

    def _calculate_emergency_fund_months(self, user_id: str) -> float:
        """
        Calculate how many months of expenses are covered by potential savings.
        
        This is a simplified calculation based on:
        - Monthly income
        - Average monthly expenses
        - Assumes savings = income - expenses (if positive)
        """
        persona = self._persona_agent.get_persona(user_id)
        monthly_income = persona.get("monthly_income") or 0
        
        if monthly_income == 0:
            return 0.0
        
        # Get prediction data for expense info
        prediction = self._prediction_agent.predict_financial_risk(user_id)
        avg_daily_expense = prediction.get("avg_daily_expense", 0)
        monthly_expense = avg_daily_expense * 30
        
        if monthly_expense == 0:
            # No expenses recorded yet, assume full income can be saved
            return 6.0  # Assume healthy position
        
        # Calculate monthly savings
        monthly_savings = monthly_income - monthly_expense
        
        if monthly_savings <= 0:
            return 0.0  # Not saving anything
        
        # Rough estimate: how many months of expenses could be saved in a year
        # This is a simplification - in reality would track actual savings
        potential_savings = monthly_savings * 3  # 3 months of saving
        months_covered = potential_savings / monthly_expense
        
        return min(months_covered, 12.0)  # Cap at 12 months

    def _get_risk_profile(self, risk_level: Optional[str]) -> str:
        """Map risk level to profile name."""
        if risk_level == "low":
            return "conservative"
        elif risk_level == "high":
            return "aggressive"
        else:
            return "balanced"

    def get_allocation_strategy(self, user_id: str) -> dict:
        """
        Get recommended investment allocation strategy.
        
        The strategy is based on:
        1. User's risk tolerance
        2. Primary financial goal
        3. Emergency fund status
        
        Args:
            user_id: The user identifier
            
        Returns:
            Dictionary with allocation strategy:
            {
                "equity": int (percentage),
                "debt": int (percentage),
                "emergency_fund": int (percentage),
                "rationale": list of strings explaining decisions,
                "warnings": list of any concerns,
                "persona_summary": dict with relevant persona info
            }
        """
        # Get persona data
        persona = self._persona_agent.get_persona(user_id)
        monthly_income = persona.get("monthly_income")
        risk_level = persona.get("risk_level")
        primary_goal = persona.get("primary_goal")
        
        # Initialize result
        result = {
            "equity": 0,
            "debt": 0,
            "emergency_fund": 0,
            "rationale": [],
            "warnings": [],
            "persona_summary": {
                "monthly_income": monthly_income,
                "risk_level": risk_level,
                "primary_goal": primary_goal
            }
        }
        
        # Check if we have enough data
        if not monthly_income:
            result["warnings"].append("Monthly income not set - cannot provide personalized strategy")
            result["equity"] = 33
            result["debt"] = 34
            result["emergency_fund"] = 33
            result["rationale"].append("Using default balanced allocation due to missing income data")
            return result
        
        # Step 1: Start with base allocation based on risk profile
        risk_profile = self._get_risk_profile(risk_level)
        base_allocation = self.ALLOCATION_TEMPLATES[risk_profile].copy()
        
        result["equity"] = base_allocation["equity"]
        result["debt"] = base_allocation["debt"]
        result["emergency_fund"] = base_allocation["emergency_fund"]
        result["rationale"].append(f"Base allocation: {risk_profile} profile (risk level: {risk_level or 'medium'})")
        
        # Step 2: Check emergency fund status
        emergency_months = self._calculate_emergency_fund_months(user_id)
        
        if emergency_months < 3:
            # Priority: Build emergency fund first
            emergency_boost = 15
            result["emergency_fund"] = min(result["emergency_fund"] + emergency_boost, 50)
            
            # Reduce equity more than debt for safety
            equity_reduction = min(result["equity"], 10)
            debt_reduction = emergency_boost - equity_reduction
            
            result["equity"] = max(result["equity"] - equity_reduction, 10)
            result["debt"] = max(result["debt"] - debt_reduction, 10)
            
            result["rationale"].append(
                f"Emergency fund priority: Less than 3 months coverage detected. "
                f"Increased emergency fund allocation by {emergency_boost}%."
            )
            result["warnings"].append(
                "Your emergency fund appears insufficient. Consider building 3-6 months of expenses before aggressive investing."
            )
        elif emergency_months >= 6:
            # Good emergency fund - can reduce allocation
            result["rationale"].append(
                f"Emergency fund healthy: ~{emergency_months:.1f} months coverage. "
                "Can allocate more to growth."
            )
        
        # Step 3: Apply goal-based adjustments
        if primary_goal and primary_goal in self.GOAL_ADJUSTMENTS:
            adjustments = self.GOAL_ADJUSTMENTS[primary_goal]
            
            result["equity"] = max(10, min(70, result["equity"] + adjustments["equity"]))
            result["debt"] = max(10, min(70, result["debt"] + adjustments["debt"]))
            result["emergency_fund"] = max(10, min(50, result["emergency_fund"] + adjustments["emergency_fund"]))
            
            goal_label = primary_goal.replace("_", " ")
            result["rationale"].append(f"Goal adjustment: Optimized for {goal_label}")
        
        # Step 4: Normalize to ensure sum = 100
        total = result["equity"] + result["debt"] + result["emergency_fund"]
        if total != 100:
            # Adjust proportionally
            factor = 100 / total
            result["equity"] = round(result["equity"] * factor)
            result["debt"] = round(result["debt"] * factor)
            result["emergency_fund"] = 100 - result["equity"] - result["debt"]
        
        # Step 5: Add general advice based on profile
        if risk_level == "low":
            result["rationale"].append(
                "Conservative approach: Focus on capital preservation with debt instruments and emergency reserves."
            )
        elif risk_level == "high":
            result["rationale"].append(
                "Growth-oriented approach: Higher equity allocation for long-term wealth building."
            )
        else:
            result["rationale"].append(
                "Balanced approach: Mix of growth and stability for steady progress."
            )
        
        return result

    def get_strategy_explanation(self, user_id: str) -> dict:
        """
        Get a detailed explanation of the investment strategy.
        
        This method provides both numeric allocation and explanations
        suitable for display to the user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Dictionary with strategy and formatted explanations
        """
        strategy = self.get_allocation_strategy(user_id)
        
        # Build explanation text
        explanation_parts = []
        
        explanation_parts.append(
            f"Based on your profile, here's your recommended allocation:\n"
            f"• **Equity (stocks/mutual funds):** {strategy['equity']}%\n"
            f"• **Debt (bonds/FDs):** {strategy['debt']}%\n"
            f"• **Emergency Fund:** {strategy['emergency_fund']}%"
        )
        
        if strategy["rationale"]:
            explanation_parts.append("\n**Why this allocation:**")
            for i, reason in enumerate(strategy["rationale"], 1):
                explanation_parts.append(f"{i}. {reason}")
        
        if strategy["warnings"]:
            explanation_parts.append("\n**⚠️ Important considerations:**")
            for warning in strategy["warnings"]:
                explanation_parts.append(f"• {warning}")
        
        strategy["explanation"] = "\n".join(explanation_parts)
        
        return strategy


# Singleton instance
_investment_agent: Optional[InvestmentStrategyAgent] = None


def get_investment_agent() -> InvestmentStrategyAgent:
    """Get the singleton InvestmentStrategyAgent instance."""
    global _investment_agent
    if _investment_agent is None:
        _investment_agent = InvestmentStrategyAgent()
    return _investment_agent
