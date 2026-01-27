"""LLM Client for generating natural language responses using Groq."""

import os
from typing import Optional
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env in project root (parent of backend)
    env_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(env_path)
    print(f"[LLM Client] Loaded .env from: {env_path}")
except ImportError:
    print("[LLM Client] python-dotenv not installed, using system env vars only")

# Try to import Groq, but make it optional
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class LLMClient:
    """
    Minimal LLM client for generating conversational responses.
    
    Uses Groq API. Falls back to a simple response if unavailable.
    """

    SYSTEM_PROMPT = """You are a helpful financial planning assistant. Your role is to:
- Help users understand financial concepts
- Provide general guidance on budgeting, saving, and investing
- Be friendly and encouraging about financial health

Important rules:
- Do NOT make up specific numbers, rates, or financial data
- Do NOT claim to have performed any actions (like saving expenses)
- Do NOT provide specific investment advice or guarantees
- If asked to do something, explain that you can help and guide them on how to proceed
- Keep responses concise and helpful
- If you don't know something, say so honestly"""

    def __init__(self):
        """Initialize the LLM client."""
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.client = None
        
        # Debug logging
        print(f"[LLM Client] GROQ_AVAILABLE: {GROQ_AVAILABLE}")
        print(f"[LLM Client] API Key set: {bool(self.api_key)}")
        
        if GROQ_AVAILABLE and self.api_key:
            self.client = Groq(api_key=self.api_key)
            print(f"[LLM Client] Groq client initialized with model: {self.model_name}")
        else:
            if not GROQ_AVAILABLE:
                print("[LLM Client] Groq package not installed. Run: pip install groq")
            if not self.api_key:
                print("[LLM Client] GROQ_API_KEY not set in environment")

    def is_available(self) -> bool:
        """Check if LLM is available for use."""
        return self.client is not None

    def generate_response(
        self,
        message: str,
        persona_context: Optional[dict] = None
    ) -> str:
        """
        Generate a response using the LLM.
        
        Args:
            message: The user's message
            persona_context: Optional dict with user's persona data
                             (monthly_income, risk_level, primary_goal)
        
        Returns:
            Generated response string
        """
        if not self.is_available():
            return self._fallback_response(message)

        # Build context message
        context_parts = []
        if persona_context:
            if persona_context.get("monthly_income"):
                context_parts.append(f"User's monthly income: ₹{persona_context['monthly_income']:,.0f}")
            if persona_context.get("risk_level"):
                context_parts.append(f"Risk tolerance: {persona_context['risk_level']}")
            if persona_context.get("primary_goal"):
                context_parts.append(f"Primary financial goal: {persona_context['primary_goal']}")

        # Build system message with context
        system_message = self.SYSTEM_PROMPT
        if context_parts:
            system_message += f"\n\nUser context:\n" + "\n".join(context_parts)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Log error in production, return fallback for now
            print(f"LLM error: {e}")
            return self._fallback_response(message)

    def _fallback_response(self, message: str) -> str:
        """Fallback response when LLM is unavailable."""
        return (
            "I understand you're asking about financial planning. "
            "I can help you with:\n"
            "• Setting your monthly income (e.g., 'My income is 50000 per month')\n"
            "• Tracking expenses (e.g., 'Spent 500 on groceries')\n"
            "• Budget planning (e.g., 'Help me with my budget')\n"
            "• Investment guidance (e.g., 'How should I invest?')\n\n"
            "What would you like to do?"
        )


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create the LLM client singleton."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def llm_respond(message: str, persona_context: Optional[dict] = None) -> str:
    """
    Convenience function to generate an LLM response.
    
    Args:
        message: The user's message
        persona_context: Optional persona data dict
        
    Returns:
        Generated response string
    """
    client = get_llm_client()
    return client.generate_response(message, persona_context)
