"""
config.py
---------
Loads secrets from .env and holds all static configuration / form options
used across the FinWise AI app. No AI or business logic lives here.
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file (if present) into the environment
load_dotenv()


def _get_secret(name: str, default: str = "") -> str:
    """Read a secret from the environment first, then fall back to
    Streamlit's secrets manager (st.secrets). This makes the app work
    both locally (via a .env file) and on Streamlit Community Cloud,
    where secrets are configured in the app dashboard instead of a
    committed .env file.
    """
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
        return st.secrets.get(name, default)
    except Exception:
        return default


# ---------------------------------------------------------------------------
# OpenAI / LLM settings
# ---------------------------------------------------------------------------
OPENAI_API_KEY = _get_secret("OPENAI_API_KEY", "")
DEFAULT_MODEL = _get_secret("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_TEMPERATURE = 0.3

# ---------------------------------------------------------------------------
# App metadata
# ---------------------------------------------------------------------------
APP_TITLE = "FinWise AI"
APP_TAGLINE = "AI-Powered Personal Financial Analysis & Smart Budget Assistant"

EDUCATIONAL_DISCLAIMER = (
    "⚠️ **Educational use only.** FinWise AI is a learning prototype. It does "
    "not provide guaranteed investment advice, cannot execute financial "
    "transactions, and is not connected to any real bank account. Nothing "
    "shown here is financial advice — please consult a qualified financial "
    "professional before making real money decisions."
)

# ---------------------------------------------------------------------------
# Form options
# ---------------------------------------------------------------------------

# Internal key -> label shown on screen
EXPENSE_CATEGORIES = {
    "housing": "Housing / Rent",
    "food": "Food",
    "transportation": "Transportation",
    "utilities": "Utilities",
    "education": "Education",
    "healthcare": "Healthcare",
    "entertainment": "Entertainment",
    "loan_debt": "Loan / Debt Payments",
    "other": "Other",
}

FINANCIAL_GOALS = [
    "Save money",
    "Build an emergency fund",
    "Pay off debt",
    "Save for a vacation",
    "Start a business",
    "Improve budgeting habits",
]

CURRENCIES = ["USD", "EUR", "GBP", "PKR", "INR", "AED", "CAD", "AUD"]

CACHE_OPTIONS = {
    "In-Memory (fast, cleared on restart)": "memory",
    "SQLite (persists across restarts)": "sqlite",
    "No caching": "none",
}

SQLITE_CACHE_PATH = ".finwise_cache.db"

# Financial health score bands (for display only - purely educational)
SCORE_BANDS = [
    (80, 100, "Strong", "success"),
    (60, 79, "Generally Healthy", "info"),
    (40, 59, "Needs Improvement", "warning"),
    (0, 39, "High Attention", "error"),
]


def get_score_band(score: int):
    """Return (label, streamlit_status) for a given 0-100 score."""
    for low, high, label, status in SCORE_BANDS:
        if low <= score <= high:
            return label, status
    return "Unknown", "info"
