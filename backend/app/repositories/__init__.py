"""Repository layer for database access.

Repositories contain all database access logic and return plain Python objects/dicts.
They have no agent or business logic - just data access.
"""

from app.repositories.expense_repo import (
    add_expense,
    get_expenses,
    get_expenses_by_category,
    get_total_spending,
    clear_expenses
)

from app.repositories.persona_repo import (
    get_persona,
    upsert_persona,
    get_or_create_user
)

from app.repositories.budget_repo import (
    get_budgets,
    get_budget_by_category,
    upsert_budget,
    delete_budget
)

__all__ = [
    # Expense
    "add_expense",
    "get_expenses",
    "get_expenses_by_category",
    "get_total_spending",
    "clear_expenses",
    # Persona
    "get_persona",
    "upsert_persona",
    "get_or_create_user",
    # Budget
    "get_budgets",
    "get_budget_by_category",
    "upsert_budget",
    "delete_budget",
]
