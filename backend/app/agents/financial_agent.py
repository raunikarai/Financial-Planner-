"""Financial Planner Agent - Simple deterministic agent for financial guidance."""

import re
from typing import Optional, Tuple

from app.tools.expense_tools import add_expense
from app.memory.persona_store import (
    get_persona, set_income, set_risk_level, set_primary_goal, get_missing_fields
)
from app.services.llm_client import llm_respond


class FinancialPlannerAgent:
    """A minimal financial planning agent that provides helpful responses."""

    # Common expense categories for detection
    EXPENSE_CATEGORIES = [
        "food", "groceries", "rent", "transport", "transportation",
        "entertainment", "utilities", "shopping", "health", "medical",
        "education", "travel", "clothing", "dining", "restaurant"
    ]

    # Risk level keywords
    RISK_LEVELS = {
        "low": ["low risk", "safe", "conservative", "stable", "no risk", "minimal risk"],
        "medium": ["medium risk", "moderate", "balanced", "some risk"],
        "high": ["high risk", "aggressive", "risky", "high reward", "maximum growth"]
    }

    # Goal keywords
    GOALS = {
        "savings": ["save", "saving", "savings", "emergency fund"],
        "investment": ["invest", "investment", "grow wealth", "wealth building"],
        "debt_repayment": ["debt", "loan", "pay off", "repay", "clear debt"],
        "retirement": ["retire", "retirement", "pension"],
        "education": ["education", "study", "college", "school fee"]
    }

    def _parse_income(self, message: str) -> Optional[float]:
        """Extract income amount from message."""
        message_lower = message.lower()
        
        # Check for income keywords
        income_keywords = ["income", "salary", "earn", "make", "per month", "monthly"]
        if not any(kw in message_lower for kw in income_keywords):
            return None
        
        # Extract number (support formats like 40000, 40,000, 40k)
        # First try to find "k" notation
        k_match = re.search(r'(\d+(?:\.\d+)?)\s*k', message_lower)
        if k_match:
            return float(k_match.group(1)) * 1000
        
        # Try regular number - remove commas first for clean parsing
        clean_message = message.replace(',', '')
        num_match = re.search(r'(\d+(?:\.\d+)?)', clean_message)
        if num_match:
            return float(num_match.group(1))
        
        return None

    def _should_use_llm(self, message: str) -> bool:
        """Check if the message should be handled by LLM (questions, confusion, explanations)."""
        message_lower = message.lower().strip()
        
        # Question starters
        question_starters = ["what", "how", "why", "when", "where", "which", "can", "could", "should", "is", "are", "do", "does"]
        
        # Phrases that indicate user wants explanation/information
        explanation_phrases = [
            "confused", "don't understand", "explain", "tell me about", 
            "what's the difference", "i need to know", "unclear", 
            "not sure", "wondering", "curious", "learn about"
        ]
        
        return (
            message_lower.endswith("?") or
            any(message_lower.startswith(q) for q in question_starters) or
            any(phrase in message_lower for phrase in explanation_phrases)
        )

    def _parse_risk_level(self, message: str) -> Optional[str]:
        """Extract risk level from message."""
        # Don't parse if it should go to LLM
        if self._should_use_llm(message):
            return None
            
        message_lower = message.lower()
        
        # Look for declaration patterns
        declaration_patterns = ["i prefer", "i want", "i like", "my risk", "i'm", "i am"]
        has_declaration = any(p in message_lower for p in declaration_patterns)
        
        if not has_declaration:
            return None
        
        for level, keywords in self.RISK_LEVELS.items():
            if any(kw in message_lower for kw in keywords):
                return level
        return None

    def _parse_goal(self, message: str) -> Optional[str]:
        """Extract primary financial goal from message."""
        # Don't parse if it's a question
        if self._should_use_llm(message):
            return None
            
        message_lower = message.lower()
        
        # Look for declaration patterns
        declaration_patterns = ["i want to", "my goal", "i need to", "i plan to", "goal is", "i'm planning"]
        has_declaration = any(p in message_lower for p in declaration_patterns)
        
        if not has_declaration:
            return None
        
        for goal, keywords in self.GOALS.items():
            if any(kw in message_lower for kw in keywords):
                return goal
        return None

    def _parse_expense(self, message: str) -> Optional[Tuple[float, str, Optional[str]]]:
        """
        Parse expense information from a message.
        
        Looks for patterns like:
        - "spent 250 on food"
        - "paid 100 for groceries"
        - "bought food for 50"
        
        Returns:
            Tuple of (amount, category, note) if found, None otherwise
        """
        message_lower = message.lower()
        
        # Check for expense keywords
        expense_keywords = ["spent", "paid", "bought", "expense", "cost me"]
        if not any(kw in message_lower for kw in expense_keywords):
            return None
        
        # Extract amount (look for numbers)
        amount_match = re.search(r'(\d+(?:\.\d{1,2})?)', message)
        if not amount_match:
            return None
        amount = float(amount_match.group(1))
        
        # Extract category
        category = "other"
        for cat in self.EXPENSE_CATEGORIES:
            if cat in message_lower:
                category = cat
                break
        
        # Use the original message as note (simplified)
        note = message.strip() if len(message) > 0 else None
        
        return (amount, category, note)

    def respond(self, message: str) -> str:
        """
        Generate a finance-related response based on user message.
        
        Args:
            message: The user's input message
            
        Returns:
            A helpful finance-related response string
        """
        message_lower = message.lower()
        persona = get_persona("default")

        # Check for income update
        income = self._parse_income(message)
        if income is not None:
            set_income(income, "default")
            response = f"Got it! 👍 I'll base suggestions on ₹{income:,.0f} monthly income."
            # Prompt for next missing field
            missing = get_missing_fields("default")
            if "risk_level" in missing:
                response += "\n\nNow, what's your risk tolerance? (low/conservative, medium/balanced, or high/aggressive)"
            elif "primary_goal" in missing:
                response += "\n\nWhat's your primary financial goal? (savings, investment, debt repayment, retirement)"
            return response

        # Check for risk level update
        risk_level = self._parse_risk_level(message)
        if risk_level is not None:
            set_risk_level(risk_level, "default")
            response = f"Noted! I've set your risk tolerance to {risk_level}."
            # Prompt for next missing field
            missing = get_missing_fields("default")
            if "primary_goal" in missing:
                response += "\n\nWhat's your primary financial goal? (savings, investment, debt repayment, retirement)"
            return response

        # Check for goal update
        goal = self._parse_goal(message)
        if goal is not None:
            set_primary_goal(goal, "default")
            response = f"Great! I've noted your primary goal as {goal.replace('_', ' ')}."
            if persona.monthly_income:
                response += f"\n\nWith your ₹{persona.monthly_income:,.0f} monthly income, I can now provide personalized recommendations!"
            return response

        # Check for expense intake
        expense_data = self._parse_expense(message)
        if expense_data:
            amount, category, note = expense_data
            expense = add_expense(amount=amount, category=category, note=note)
            response = (
                f"Got it! I've recorded your expense:\n"
                f"• Amount: ₹{amount:,.2f}\n"
                f"• Category: {category.capitalize()}"
            )
            # Add personalized context if income is known
            if persona.monthly_income:
                percentage = (amount / persona.monthly_income) * 100
                response += f"\n\nThis is {percentage:.1f}% of your monthly income."
            response += "\n\nWould you like to add another or see your spending summary?"
            return response

        # Check for greetings - only match if it's a simple greeting, not a question
        if not self._should_use_llm(message):
            greeting_words = ["hello", "hi", "hey"]
            # Check if message starts with greeting or is just a greeting
            is_greeting = any(
                message_lower.startswith(word) or message_lower == word 
                for word in greeting_words
            )
            if is_greeting:
                response = "Hello! I'm your Financial Planner Assistant. "
                if persona.monthly_income:
                    response += f"Welcome back! I remember your monthly income is ₹{persona.monthly_income:,.0f}. "
                    response += "How can I help you today?"
                else:
                    response += (
                        "I can help you with budgeting, expense tracking, and investment planning. "
                        "To get started, could you tell me your monthly income?"
                    )
                return response

        # Check for income-related messages
        if any(word in message_lower for word in ["income", "salary", "earn"]):
            if persona.monthly_income:
                return (
                    f"I have your monthly income recorded as ₹{persona.monthly_income:,.0f}. "
                    "Would you like to update it? Just say something like 'My income is 50000 per month'."
                )
            return (
                "Great! Knowing your income helps me create a personalized budget. "
                "Please tell me your monthly income (e.g., 'My income is 40000 per month')."
            )

        # Check for expense-related messages (only if not a question)
        if not self._should_use_llm(message):
            if any(word in message_lower for word in ["expense", "spend", "cost"]):
                return (
                    "Tracking expenses is key to financial health. "
                    "I recommend the 50/30/20 rule: 50% for needs, 30% for wants, and 20% for savings. "
                    "Would you like help setting up a budget based on this?"
                )

        # Check for budget-related messages (only if not a question)
        if not self._should_use_llm(message) and any(word in message_lower for word in ["budget", "allocate"]):
            response = "I can help you create a budget! "
            if persona.monthly_income:
                needs = persona.monthly_income * 0.5
                wants = persona.monthly_income * 0.3
                savings = persona.monthly_income * 0.2
                response += (
                    f"\n\nBased on your ₹{persona.monthly_income:,.0f} income and the 50/30/20 rule:\n"
                    f"• Needs (50%): ₹{needs:,.0f}\n"
                    f"• Wants (30%): ₹{wants:,.0f}\n"
                    f"• Savings (20%): ₹{savings:,.0f}\n\n"
                    "Would you like to customize these allocations?"
                )
            else:
                response += (
                    "First, let's identify your fixed expenses (rent, utilities, subscriptions) "
                    "and variable expenses (food, entertainment). What's your monthly income?"
                )
            return response

        # Check for investment-related messages (only if not a question)
        if not self._should_use_llm(message) and any(word in message_lower for word in ["invest", "stock", "mutual fund"]):
            response = "Investing is a great way to grow your wealth! "
            if persona.risk_level:
                if persona.risk_level == "low":
                    response += (
                        "\n\nBased on your conservative risk profile, I'd recommend:\n"
                        "• Fixed Deposits (40%)\n"
                        "• Debt Mutual Funds (40%)\n"
                        "• Large-cap Equity (20%)"
                    )
                elif persona.risk_level == "medium":
                    response += (
                        "\n\nBased on your balanced risk profile, I'd recommend:\n"
                        "• Equity Mutual Funds (50%)\n"
                        "• Debt Funds (30%)\n"
                        "• Fixed Deposits (20%)"
                    )
                else:  # high
                    response += (
                        "\n\nBased on your aggressive risk profile, I'd recommend:\n"
                        "• Equity/Stocks (60%)\n"
                        "• Equity Mutual Funds (30%)\n"
                        "• Debt Funds (10%)"
                    )
            else:
                response += (
                    "\n\nBefore recommending investments, I need to understand your risk tolerance. "
                    "Are you comfortable with high-risk high-reward investments, "
                    "or do you prefer stable, lower-return options?"
                )
            return response

        # Check for help requests (specific phrases only)
        help_phrases = ["what can you do", "features", "help me"]
        if any(phrase in message_lower for phrase in help_phrases) or message_lower.strip() == "help":
            return (
                "I can assist you with:\n"
                "1. Setting up a monthly budget\n"
                "2. Tracking your expenses\n"
                "3. Creating an investment plan\n"
                "4. Analyzing your spending patterns\n"
                "What would you like to start with?"
            )

        # No rule matched - use LLM fallback for ambiguous messages
        return self._llm_fallback(message, persona)

    def _llm_fallback(self, message: str, persona) -> str:
        """
        Use LLM to handle ambiguous messages that don't match any rule.
        
        The LLM provides conversational responses only - it does NOT
        execute tools or modify any data.
        
        Args:
            message: The user's message
            persona: The user's persona object
            
        Returns:
            LLM-generated response string
        """
        # Build persona context for LLM
        persona_context = {
            "monthly_income": persona.monthly_income,
            "risk_level": persona.risk_level,
            "primary_goal": persona.primary_goal
        }
        
        # Get LLM response
        return llm_respond(message, persona_context)
