"""Financial Planner Agent - Orchestrator for the A2A architecture."""

import re
from typing import Optional, Tuple

from app.agents.persona_agent import get_persona_agent, PersonaAgent
from app.agents.prediction_agent import get_prediction_agent, PredictionAgent
from app.agents.budget_agent import get_budget_agent, BudgetAgent
from app.agents.investment_agent import get_investment_agent, InvestmentStrategyAgent
from app.tools.expense_tools import add_expense
from app.services.llm_client import llm_respond


class FinancialPlannerAgent:
    """
    Central orchestrator agent for the Financial Planner application.
    
    This agent coordinates between PersonaAgent, PredictionAgent, BudgetAgent,
    and InvestmentStrategyAgent, handling user messages and generating responses.
    It does NOT contain any persona storage logic, prediction calculations,
    budget logic, or investment strategy logic directly.
    
    Architecture:
    - PersonaAgent: Manages user profile data
    - PredictionAgent: Handles financial forecasting
    - BudgetAgent: Evaluates budgets and detects breaches
    - InvestmentStrategyAgent: Provides investment allocation strategies
    - FinancialPlannerAgent: Orchestrates and generates responses
    """

    def __init__(self):
        """Initialize the orchestrator with references to other agents."""
        self._persona_agent: PersonaAgent = get_persona_agent()
        self._prediction_agent: PredictionAgent = get_prediction_agent()
        self._budget_agent: BudgetAgent = get_budget_agent()
        self._investment_agent: InvestmentStrategyAgent = get_investment_agent()

    # ==================== Message Parsing Methods ====================

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

    def _is_future_question(self, message: str) -> bool:
        """Check if the message is asking about future financial decisions."""
        message_lower = message.lower()
        
        future_phrases = [
            "can i afford", "can i buy", "should i buy", "should i spend",
            "do i have enough", "will i have enough", "can i splurge",
            "is it safe to", "can i purchase", "enough money for",
            "afford to", "have budget for", "room in my budget"
        ]
        
        return any(phrase in message_lower for phrase in future_phrases)

    def _is_prediction_request(self, message: str) -> bool:
        """Check if the user is asking for cashflow prediction or analysis."""
        message_lower = message.lower()
        
        prediction_phrases = [
            "predict", "forecast", "projection", "cashflow", "cash flow",
            "burn rate", "how long", "days left", "money last",
            "spending analysis", "spending summary", "financial health",
            "am i on track", "how am i doing"
        ]
        
        return any(phrase in message_lower for phrase in prediction_phrases)

    def _is_investment_query(self, message: str) -> bool:
        """Check if the user is asking about investment strategy or allocation."""
        message_lower = message.lower()
        
        investment_phrases = [
            "how should i invest", "where should i invest", "investment strategy",
            "investment allocation", "allocate my money", "how to invest",
            "invest my savings", "investment plan", "portfolio allocation",
            "how much to invest", "investment advice", "saving strategy",
            "where to put my money", "grow my money", "wealth building",
            "asset allocation", "diversify", "diversification"
        ]
        
        # Also check for question pattern with invest/save keywords
        invest_keywords = ["invest", "investing", "investment", "allocate", "allocation"]
        question_patterns = ["how", "where", "what", "should"]
        
        has_invest_keyword = any(kw in message_lower for kw in invest_keywords)
        has_question = any(q in message_lower for q in question_patterns) or message_lower.endswith("?")
        
        return any(phrase in message_lower for phrase in investment_phrases) or (has_invest_keyword and has_question)

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

    # ==================== Response Formatting Methods ====================

    def _format_prediction_insight(self, prediction: dict) -> str:
        """Convert prediction data into a human-readable insight."""
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
        
        insight_parts.append(
            f"📊 **Cashflow Analysis** ({days_remaining} days left in month)\n"
            f"• Daily income: ₹{prediction['daily_income']:,.0f}\n"
            f"• Avg daily spending: ₹{prediction['avg_daily_expense']:,.0f}"
        )
        
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

    def _format_affordability_response(self, affordability: dict, amount: float) -> str:
        """Convert affordability check into a human-readable response."""
        if affordability["expense_count"] == 0 or affordability["monthly_income"] == 0:
            return (
                "I need more information to help you decide. "
                "Please set your monthly income and log a few expenses first!"
            )
        
        recommendation = affordability["recommendation"]
        daily_savings = affordability["daily_savings"]
        days_to_save = affordability["days_to_save"]
        
        if recommendation == "yes":
            return (
                f"✅ Yes! At your current savings rate (₹{daily_savings:,.0f}/day), "
                f"you could afford ₹{amount:,.0f} in about {days_to_save} days."
            )
        elif recommendation == "caution" and affordability["can_afford"]:
            return (
                f"🤔 It's doable. You're saving ₹{daily_savings:,.0f}/day, "
                f"so ₹{amount:,.0f} would take about {days_to_save} days to save."
            )
        elif recommendation == "caution":
            return (
                f"⚠️ That's a stretch. At ₹{daily_savings:,.0f}/day savings, "
                f"it would take a while to save ₹{amount:,.0f}."
            )
        else:
            return (
                f"🚨 I'd advise caution. You're currently spending "
                f"₹{abs(affordability['daily_burn_rate']):,.0f} more than you earn daily. "
                f"Adding ₹{amount:,.0f} would strain your budget further."
            )

    def _generate_combined_warning(
        self,
        budget_eval: dict,
        prediction: dict,
        persona_risk: str,
        amount: float,
        category: str,
        monthly_income: Optional[float]
    ) -> str:
        """
        Combine signals from BudgetAgent and PredictionAgent to generate warnings.
        
        Warning levels are calibrated based on persona risk tolerance:
        - Conservative users get earlier warnings
        - Aggressive users get warnings only for critical issues
        
        Args:
            budget_eval: Result from BudgetAgent.evaluate_budget()
            prediction: Result from PredictionAgent.predict_financial_risk()
            persona_risk: User's risk tolerance (low/medium/high)
            amount: The expense amount
            category: The expense category
            monthly_income: User's monthly income (if known)
            
        Returns:
            Warning string to append to response, or empty string if no warning
        """
        warnings = []
        
        # === Add income percentage context ===
        if monthly_income:
            percentage = (amount / monthly_income) * 100
            warnings.append(f"\n\nThis is {percentage:.1f}% of your monthly income.")
        
        # === Determine warning thresholds based on risk tolerance ===
        # Conservative users: warn earlier, more detail
        # Aggressive users: warn only on critical issues
        thresholds = {
            "low": {"budget_warn": "low", "prediction_warn": "low"},
            "medium": {"budget_warn": "medium", "prediction_warn": "medium"},
            "high": {"budget_warn": "high", "prediction_warn": "high"}
        }
        user_threshold = thresholds.get(persona_risk, thresholds["medium"])
        
        # === Process Budget Signals ===
        if budget_eval["breach"]:
            severity = budget_eval["severity"]
            severity_order = ["low", "medium", "high", "critical"]
            
            # Check if severity meets user's warning threshold
            should_warn = (
                severity_order.index(severity) >= 
                severity_order.index(user_threshold["budget_warn"])
            )
            
            if should_warn or severity == "critical":
                # Determine emoji and tone based on severity
                if severity == "critical":
                    emoji = "🚨"
                    tone = "**Critical:**"
                elif severity == "high":
                    emoji = "⚠️"
                    tone = "**Warning:**"
                elif severity == "medium":
                    emoji = "📊"
                    tone = "**Note:**"
                else:
                    emoji = "ℹ️"
                    tone = "**FYI:**"
                
                # Build budget warning message
                budget_msg = f"\n\n{emoji} {tone} {budget_eval['message']}"
                
                # Add category detail if available
                if budget_eval["category_status"]:
                    cat_status = budget_eval["category_status"]
                    if cat_status["exceeded_by"] > 0:
                        budget_msg += f"\n• {category.capitalize()} spending: ₹{cat_status['spent']:,.0f} / ₹{cat_status['limit']:,.0f} ({cat_status['percentage']:.0f}%)"
                
                # Add total budget detail if available
                if budget_eval["total_status"]:
                    total_status = budget_eval["total_status"]
                    budget_msg += f"\n• Total spending: ₹{total_status['spent']:,.0f} / ₹{total_status['limit']:,.0f} ({total_status['percentage']:.0f}%)"
                
                warnings.append(budget_msg)
        
        # === Process Prediction Signals ===
        pred_risk = prediction.get("risk_level", "low")
        pred_severity_map = {"low": 0, "medium": 1, "high": 2}
        
        # Only add prediction warning if budget warning wasn't critical
        # (to avoid information overload)
        if budget_eval["severity"] != "critical":
            if pred_risk == "high" and prediction.get("projected_shortfall", 0) > 0:
                shortfall = prediction["projected_shortfall"]
                days_left = prediction.get("days_remaining_in_month", 0)
                warnings.append(
                    f"\n\n📈 **Cashflow Alert:** With {days_left} days left in the month, "
                    f"you may overspend by ₹{shortfall:,.0f} at current rate."
                )
            elif pred_risk == "medium" and persona_risk != "high":
                # Medium risk users don't need medium-level prediction warnings
                shortfall = prediction.get("projected_shortfall", 0)
                if shortfall > 0:
                    days_left = prediction.get("days_remaining_in_month", 0)
                    warnings.append(
                        f"\n\n📊 **Trend:** You're spending faster than earning. "
                        f"Projected shortfall: ₹{shortfall:,.0f} with {days_left} days left."
                    )
        
        # === Add actionable suggestion for critical/high warnings ===
        if budget_eval["severity"] in ["critical", "high"] or pred_risk == "high":
            if persona_risk == "low":
                warnings.append("\n\n💡 Consider reviewing non-essential expenses or adjusting your budget.")
            elif persona_risk == "medium":
                warnings.append("\n\n💡 You might want to slow down on discretionary spending.")
            # High-risk users don't need hand-holding suggestions
        
        return "".join(warnings)

    def _format_investment_strategy(self, strategy: dict, use_llm: bool = True) -> str:
        """
        Format investment strategy response.
        
        The allocation numbers come from InvestmentStrategyAgent and are FIXED.
        LLM is only used to provide a natural language explanation, NOT to
        modify allocation percentages.
        
        Args:
            strategy: Result from InvestmentStrategyAgent.get_allocation_strategy()
            use_llm: Whether to use LLM for explanation (default True)
            
        Returns:
            Formatted response string with allocation and explanation
        """
        # Always use deterministic allocation numbers from the agent
        allocation_text = (
            f"📊 **Recommended Investment Allocation**\n\n"
            f"• **Equity (stocks/mutual funds):** {strategy['equity']}%\n"
            f"• **Debt (bonds/FDs):** {strategy['debt']}%\n"
            f"• **Emergency Fund:** {strategy['emergency_fund']}%\n"
        )
        
        # Add warnings if any
        if strategy["warnings"]:
            allocation_text += "\n**⚠️ Important:**\n"
            for warning in strategy["warnings"]:
                allocation_text += f"• {warning}\n"
        
        # Add rationale (deterministic rules that led to this allocation)
        if strategy["rationale"]:
            allocation_text += "\n**Why this allocation:**\n"
            for i, reason in enumerate(strategy["rationale"], 1):
                allocation_text += f"{i}. {reason}\n"
        
        # Optionally use LLM to provide a conversational explanation
        # but NEVER let it change the allocation numbers
        if use_llm:
            llm_prompt = (
                f"The user asked about investment strategy. Based on their profile:\n"
                f"- Monthly income: {strategy['persona_summary'].get('monthly_income')}\n"
                f"- Risk level: {strategy['persona_summary'].get('risk_level')}\n"
                f"- Primary goal: {strategy['persona_summary'].get('primary_goal')}\n\n"
                f"I've calculated this allocation: Equity {strategy['equity']}%, "
                f"Debt {strategy['debt']}%, Emergency Fund {strategy['emergency_fund']}%.\n\n"
                f"Provide a brief, friendly 1-2 sentence explanation of why this allocation "
                f"makes sense for them. Do NOT suggest different percentages. Keep it short."
            )
            
            try:
                llm_explanation = llm_respond(llm_prompt, strategy["persona_summary"])
                if llm_explanation and len(llm_explanation) < 500:  # Sanity check
                    allocation_text += f"\n💡 **In brief:** {llm_explanation}"
            except Exception:
                # If LLM fails, we still have the deterministic response
                pass
        
        allocation_text += (
            "\n\n*Note: This is a general strategy guide, not specific product advice. "
            "Consider consulting a financial advisor for personalized recommendations.*"
        )
        
        return allocation_text

    # ==================== Main Orchestration Method ====================

    def respond(self, message: str, user_id: str = "default") -> str:
        """
        Generate a finance-related response based on user message.
        
        This is the main orchestration method that:
        1. Parses the user message
        2. Consults PersonaAgent for context
        3. Consults PredictionAgent for forecasts
        4. Uses LLM for explanations if needed
        5. Generates the final response
        
        Args:
            message: The user's input message
            user_id: The user identifier
            
        Returns:
            A helpful finance-related response string
        """
        message_lower = message.lower()
        
        # Get persona context from PersonaAgent
        persona = self._persona_agent.get_persona(user_id)

        # Check for income update
        income = self._parse_income(message)
        if income is not None:
            self._persona_agent.update_persona(user_id, {"monthly_income": income})
            response = f"Got it! 👍 I'll base suggestions on ₹{income:,.0f} monthly income."
            
            missing = self._persona_agent.get_missing_fields(user_id)
            if "risk_level" in missing:
                response += "\n\nNow, what's your risk tolerance? (low/conservative, medium/balanced, or high/aggressive)"
            elif "primary_goal" in missing:
                response += "\n\nWhat's your primary financial goal? (savings, investment, debt repayment, retirement)"
            return response

        # Check for risk level update
        risk_level = self._parse_risk_level(message)
        if risk_level is not None:
            self._persona_agent.update_persona(user_id, {"risk_level": risk_level})
            response = f"Noted! I've set your risk tolerance to {risk_level}."
            
            missing = self._persona_agent.get_missing_fields(user_id)
            if "primary_goal" in missing:
                response += "\n\nWhat's your primary financial goal? (savings, investment, debt repayment, retirement)"
            return response

        # Check for goal update
        goal = self._parse_goal(message)
        if goal is not None:
            self._persona_agent.update_persona(user_id, {"primary_goal": goal})
            response = f"Great! I've noted your primary goal as {goal.replace('_', ' ')}."
            if persona["monthly_income"]:
                response += f"\n\nWith your ₹{persona['monthly_income']:,.0f} monthly income, I can now provide personalized recommendations!"
            return response

        # Check for prediction/analysis requests - consult PredictionAgent
        if self._is_prediction_request(message):
            prediction = self._prediction_agent.predict_financial_risk(user_id)
            return self._format_prediction_insight(prediction)

        # Check for investment strategy questions - consult InvestmentStrategyAgent
        if self._is_investment_query(message):
            strategy = self._investment_agent.get_allocation_strategy(user_id)
            return self._format_investment_strategy(strategy, use_llm=True)

        # Check for future-oriented questions - consult PredictionAgent
        if self._is_future_question(message):
            amount_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d{1,2})?)', message.replace(',', ''))
            
            if amount_match:
                mentioned_amount = float(amount_match.group(1))
                affordability = self._prediction_agent.can_afford(mentioned_amount, user_id)
                return self._format_affordability_response(affordability, mentioned_amount)
            else:
                prediction = self._prediction_agent.predict_financial_risk(user_id)
                insight = self._format_prediction_insight(prediction)
                return insight + "\n\nLet me know the specific amount you're considering, and I can give you a better answer!"

        # Check for expense intake
        expense_data = self._parse_expense(message)
        if expense_data:
            amount, category, note = expense_data
            add_expense(amount=amount, category=category, note=note)
            response = (
                f"Got it! I've recorded your expense:\n"
                f"• Amount: ₹{amount:,.2f}\n"
                f"• Category: {category.capitalize()}"
            )
            
            # === Consult all agents for comprehensive assessment ===
            
            # 1. BudgetAgent: Check for budget breaches
            budget_eval = self._budget_agent.evaluate_budget(user_id, category, amount)
            
            # 2. PredictionAgent: Get cashflow risk assessment
            prediction = self._prediction_agent.predict_financial_risk(user_id)
            
            # 3. PersonaAgent: Get user's risk tolerance for calibration
            persona_risk = persona.get("risk_level", "medium")
            
            # === Combine signals and decide warning level ===
            warning_response = self._generate_combined_warning(
                budget_eval=budget_eval,
                prediction=prediction,
                persona_risk=persona_risk,
                amount=amount,
                category=category,
                monthly_income=persona.get("monthly_income")
            )
            
            if warning_response:
                response += warning_response
            
            response += "\n\nWould you like to add another expense or see your full spending analysis?"
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
                if persona["monthly_income"]:
                    response += f"Welcome back! I remember your monthly income is ₹{persona['monthly_income']:,.0f}. "
                    response += "How can I help you today?"
                else:
                    response += (
                        "I can help you with budgeting, expense tracking, and investment planning. "
                        "To get started, could you tell me your monthly income?"
                    )
                return response

        # Check for income-related messages
        if any(word in message_lower for word in ["income", "salary", "earn"]):
            if persona["monthly_income"]:
                return (
                    f"I have your monthly income recorded as ₹{persona['monthly_income']:,.0f}. "
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
            if persona["monthly_income"]:
                needs = persona["monthly_income"] * 0.5
                wants = persona["monthly_income"] * 0.3
                savings = persona["monthly_income"] * 0.2
                response += (
                    f"\n\nBased on your ₹{persona['monthly_income']:,.0f} income and the 50/30/20 rule:\n"
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

        # Check for investment-related statements (declarative, not questions)
        # Questions about investing are handled by _is_investment_query above
        if not self._should_use_llm(message) and any(word in message_lower for word in ["invest", "stock", "mutual fund"]):
            # Use InvestmentStrategyAgent for proper allocation
            strategy = self._investment_agent.get_allocation_strategy(user_id)
            
            response = "Investing is a great way to grow your wealth!\n\n"
            
            if not strategy["persona_summary"].get("monthly_income"):
                response += (
                    "To give you a personalized investment strategy, I need to know a bit more about you. "
                    "What's your monthly income?"
                )
            elif not strategy["persona_summary"].get("risk_level"):
                response += (
                    "Before I can recommend an allocation, I need to understand your risk tolerance. "
                    "Are you comfortable with high-risk high-reward investments, "
                    "or do you prefer stable, lower-return options?"
                )
            else:
                response = self._format_investment_strategy(strategy, use_llm=False)
            
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

    def _llm_fallback(self, message: str, persona: dict) -> str:
        """
        Use LLM to handle ambiguous messages that don't match any rule.
        
        The LLM provides conversational responses only - it does NOT
        execute tools or modify any data.
        """
        persona_context = {
            "monthly_income": persona["monthly_income"],
            "risk_level": persona["risk_level"],
            "primary_goal": persona["primary_goal"]
        }
        
        return llm_respond(message, persona_context)
