"""Agents package for the Financial Planner application.

A2A Architecture:
- FinancialPlannerAgent: Central orchestrator that coordinates other agents
- PersonaAgent: Manages user profile and preferences
- PredictionAgent: Handles financial forecasting and risk assessment
- BudgetAgent: Evaluates budgets and detects breaches
- InvestmentStrategyAgent: Provides investment allocation strategies
"""

from app.agents.financial_agent import FinancialPlannerAgent
from app.agents.persona_agent import PersonaAgent, get_persona_agent
from app.agents.prediction_agent import PredictionAgent, get_prediction_agent
from app.agents.budget_agent import BudgetAgent, get_budget_agent
from app.agents.investment_agent import InvestmentStrategyAgent, get_investment_agent

__all__ = [
    "FinancialPlannerAgent",
    "PersonaAgent",
    "get_persona_agent",
    "PredictionAgent",
    "get_prediction_agent",
    "BudgetAgent",
    "get_budget_agent",
    "InvestmentStrategyAgent",
    "get_investment_agent",
]