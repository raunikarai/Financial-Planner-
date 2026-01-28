"""Budget Agent for the A2A architecture.

Responsible for budget evaluation and breach detection.
All logic is deterministic and explainable - no ML or forecasting.
Uses repositories for data access - no in-memory storage.
"""

from typing import Optional
from app.repositories import expense_repo, budget_repo, persona_repo


# Default category budgets as percentage of income
DEFAULT_CATEGORY_PERCENTAGES = {
    "food": 0.15,           # 15% of income
    "groceries": 0.10,      # 10% of income
    "rent": 0.30,           # 30% of income
    "transport": 0.10,      # 10% of income
    "transportation": 0.10,
    "entertainment": 0.05,  # 5% of income
    "utilities": 0.05,      # 5% of income
    "shopping": 0.05,       # 5% of income
    "health": 0.05,         # 5% of income
    "medical": 0.05,
    "education": 0.05,      # 5% of income
    "travel": 0.05,         # 5% of income
    "clothing": 0.03,       # 3% of income
    "dining": 0.05,         # 5% of income
    "restaurant": 0.05,
    "other": 0.10,          # 10% of income
}


class BudgetAgent:
    """
    Agent responsible for budget evaluation and breach detection.
    
    This agent:
    - Evaluates category-wise and overall spending against budgets
    - Detects threshold breaches when expenses are added
    - Returns structured results (no natural language)
    
    All logic is deterministic and explainable.
    """

    def __init__(self):
        """Initialize the BudgetAgent."""
        pass

    # ==================== Budget Management ====================

    def set_category_budget(self, user_id: str, category: str, limit: float) -> dict:
        """
        Set a budget limit for a specific category.
        
        Args:
            user_id: The user identifier
            category: The expense category
            limit: The budget limit for this category
            
        Returns:
            Dict confirming the budget was set
        """
        budget_repo.upsert_budget(user_id, category.lower(), limit)
        
        return {
            "success": True,
            "category": category.lower(),
            "limit": limit
        }

    def set_total_budget(self, user_id: str, limit: float) -> dict:
        """
        Set a total monthly budget limit.
        
        Args:
            user_id: The user identifier
            limit: The total budget limit
            
        Returns:
            Dict confirming the budget was set
        """
        budget_repo.upsert_budget(user_id, "total", limit)
        
        return {
            "success": True,
            "total_limit": limit
        }

    def get_budgets(self, user_id: str) -> dict:
        """
        Get all budget limits for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Dict with category_limits and total_limit
        """
        return budget_repo.get_budgets(user_id)

    def _get_category_limit(self, user_id: str, category: str) -> Optional[float]:
        """
        Get the budget limit for a category.
        Falls back to default percentage of income if not explicitly set.
        """
        category = category.lower()
        
        # Check explicit limit first
        explicit_limit = budget_repo.get_budget_by_category(user_id, category)
        if explicit_limit is not None:
            return explicit_limit
        
        # Fall back to default percentage of income
        persona = persona_repo.get_persona(user_id)
        monthly_income = persona.get("monthly_income")
        if monthly_income and category in DEFAULT_CATEGORY_PERCENTAGES:
            return monthly_income * DEFAULT_CATEGORY_PERCENTAGES[category]
        
        return None

    def _get_total_limit(self, user_id: str) -> Optional[float]:
        """
        Get the total budget limit.
        Falls back to monthly income if not explicitly set.
        """
        # Check explicit limit first
        explicit_limit = budget_repo.get_budget_by_category(user_id, "total")
        if explicit_limit is not None:
            return explicit_limit
        
        # Fall back to monthly income
        persona = persona_repo.get_persona(user_id)
        return persona.get("monthly_income")

    # ==================== Spending Calculation ====================

    def _get_category_spending(self, user_id: str, category: str) -> float:
        """Calculate total spending for a category."""
        return expense_repo.get_total_spending(user_id, category)

    def _get_total_spending(self, user_id: str) -> float:
        """Calculate total spending across all categories."""
        return expense_repo.get_total_spending(user_id)

    # ==================== Main Evaluation Method ====================

    def evaluate_budget(
        self, 
        user_id: str, 
        category: str, 
        amount: float
    ) -> dict:
        """
        Evaluate budget impact of an expense.
        
        This is the main method called by the orchestrator after adding an expense.
        It checks for category-wise and overall budget breaches.
        
        Args:
            user_id: The user identifier
            category: The expense category
            amount: The expense amount
            
        Returns:
            Structured dict with breach information:
            {
                "breach": bool,
                "severity": "none" | "low" | "medium" | "high" | "critical",
                "type": "none" | "category" | "total" | "both",
                "category_status": {...},
                "total_status": {...},
                "message": str
            }
        """
        category = category.lower()
        result = {
            "breach": False,
            "severity": "none",
            "type": "none",
            "category_status": None,
            "total_status": None,
            "message": ""
        }
        
        breaches = []
        
        # === Check Category Budget ===
        category_limit = self._get_category_limit(user_id, category)
        if category_limit:
            category_spent = self._get_category_spending(user_id, category)
            category_percentage = (category_spent / category_limit) * 100
            
            result["category_status"] = {
                "category": category,
                "spent": category_spent,
                "limit": category_limit,
                "percentage": round(category_percentage, 1),
                "remaining": max(0, category_limit - category_spent),
                "exceeded_by": max(0, category_spent - category_limit)
            }
            
            if category_spent > category_limit:
                breaches.append({
                    "type": "category",
                    "severity": self._calculate_category_severity(category_percentage),
                    "message": f"{category.capitalize()} budget exceeded by ₹{category_spent - category_limit:,.0f}"
                })
            elif category_percentage >= 80:
                breaches.append({
                    "type": "category",
                    "severity": "low",
                    "message": f"{category.capitalize()} budget at {category_percentage:.0f}% (₹{category_limit - category_spent:,.0f} remaining)"
                })
        
        # === Check Total Budget ===
        total_limit = self._get_total_limit(user_id)
        if total_limit:
            total_spent = self._get_total_spending(user_id)
            total_percentage = (total_spent / total_limit) * 100
            
            result["total_status"] = {
                "spent": total_spent,
                "limit": total_limit,
                "percentage": round(total_percentage, 1),
                "remaining": max(0, total_limit - total_spent),
                "exceeded_by": max(0, total_spent - total_limit)
            }
            
            if total_spent > total_limit:
                breaches.append({
                    "type": "total",
                    "severity": "critical",
                    "message": f"Monthly budget exceeded by ₹{total_spent - total_limit:,.0f}"
                })
            elif total_percentage >= 100:
                breaches.append({
                    "type": "total",
                    "severity": "critical",
                    "message": f"Monthly budget at 100%"
                })
            elif total_percentage >= 80:
                breaches.append({
                    "type": "total",
                    "severity": "high" if total_percentage >= 90 else "medium",
                    "message": f"Monthly budget at {total_percentage:.0f}% (₹{total_limit - total_spent:,.0f} remaining)"
                })
        
        # === Aggregate Results ===
        if breaches:
            result["breach"] = True
            
            # Determine overall type
            types = set(b["type"] for b in breaches)
            if "category" in types and "total" in types:
                result["type"] = "both"
            elif "category" in types:
                result["type"] = "category"
            else:
                result["type"] = "total"
            
            # Use highest severity
            severity_order = ["low", "medium", "high", "critical"]
            highest_severity = max(
                breaches, 
                key=lambda b: severity_order.index(b["severity"]) if b["severity"] in severity_order else -1
            )
            result["severity"] = highest_severity["severity"]
            
            # Combine messages
            result["message"] = "; ".join(b["message"] for b in breaches)
        
        return result

    def _calculate_category_severity(self, percentage: float) -> str:
        """
        Calculate severity based on how much category budget is exceeded.
        
        Args:
            percentage: Spending as percentage of budget
            
        Returns:
            Severity level: "low", "medium", "high", "critical"
        """
        if percentage >= 150:
            return "critical"
        elif percentage >= 125:
            return "high"
        elif percentage >= 110:
            return "medium"
        else:
            return "low"

    # ==================== Budget Summary ====================

    def get_budget_summary(self, user_id: str) -> dict:
        """
        Get a complete budget summary for a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Dict with overall budget health and per-category breakdown
        """
        total_limit = self._get_total_limit(user_id)
        total_spent = self._get_total_spending(user_id)
        
        # Get all categories from expenses via repository
        expenses = expense_repo.get_expenses(user_id)
        categories = set(exp["category"] for exp in expenses)
        
        category_breakdown = {}
        for cat in categories:
            limit = self._get_category_limit(user_id, cat)
            spent = self._get_category_spending(user_id, cat)
            
            category_breakdown[cat] = {
                "spent": spent,
                "limit": limit,
                "percentage": round((spent / limit) * 100, 1) if limit else None,
                "status": self._get_status(spent, limit) if limit else "no_budget"
            }
        
        return {
            "total": {
                "spent": total_spent,
                "limit": total_limit,
                "percentage": round((total_spent / total_limit) * 100, 1) if total_limit else None,
                "status": self._get_status(total_spent, total_limit) if total_limit else "no_budget"
            },
            "categories": category_breakdown,
            "health": self._calculate_health(total_spent, total_limit)
        }

    def _get_status(self, spent: float, limit: float) -> str:
        """Get status string based on spending vs limit."""
        if not limit:
            return "no_budget"
        percentage = (spent / limit) * 100
        if percentage >= 100:
            return "exceeded"
        elif percentage >= 80:
            return "warning"
        elif percentage >= 50:
            return "on_track"
        else:
            return "healthy"

    def _calculate_health(self, spent: float, limit: float) -> str:
        """Calculate overall budget health."""
        if not limit:
            return "unknown"
        percentage = (spent / limit) * 100
        if percentage >= 100:
            return "critical"
        elif percentage >= 90:
            return "poor"
        elif percentage >= 80:
            return "fair"
        elif percentage >= 50:
            return "good"
        else:
            return "excellent"


# Singleton instance
_budget_agent: Optional[BudgetAgent] = None


def get_budget_agent() -> BudgetAgent:
    """Get the singleton BudgetAgent instance."""
    global _budget_agent
    if _budget_agent is None:
        _budget_agent = BudgetAgent()
    return _budget_agent
