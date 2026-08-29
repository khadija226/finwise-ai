"""
utils.py
--------
Small helpers: safe JSON parsing from LLM output, and a fallback
response used if the model ever returns malformed JSON.
"""

import json
import re
from typing import Optional, Dict, Any

REQUIRED_KEYS = [
    "financial_summary",
    "financial_health_score",
    "spending_analysis",
    "risk_level",
    "top_priorities",
    "budget_recommendations",
    "savings_strategy",
    "next_month_action_plan",
]


def _strip_code_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` fences if the model added them anyway."""
    text = text.strip()
    fence_match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    return text


def safe_parse_json(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    Attempt to safely parse the LLM's JSON output.
    Returns a dict on success, or None if parsing/validation fails.
    """
    if not raw_text:
        return None

    cleaned = _strip_code_fences(raw_text)

    # Try direct parse first
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Fall back: try to grab the first {...} block in the text
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    if not isinstance(data, dict):
        return None

    # Validate required keys exist
    for key in REQUIRED_KEYS:
        if key not in data:
            return None

    # Basic type coercion / safety
    try:
        data["financial_health_score"] = int(data["financial_health_score"])
    except (ValueError, TypeError):
        data["financial_health_score"] = 0

    data["financial_health_score"] = max(0, min(100, data["financial_health_score"]))

    if data.get("risk_level") not in ("LOW", "MEDIUM", "HIGH"):
        data["risk_level"] = "MEDIUM"

    return data


def fallback_response(preliminary_score: int) -> Dict[str, Any]:
    """Used only if the AI response cannot be parsed at all, so the UI never crashes."""
    return {
        "financial_summary": (
            "We couldn't generate a full AI analysis this time, so here is a "
            "basic summary based on your rule-based score only."
        ),
        "financial_health_score": preliminary_score,
        "spending_analysis": [
            {
                "category": "General",
                "observation": "AI response unavailable.",
                "recommendation": "Please try again in a moment.",
            }
        ],
        "risk_level": "MEDIUM",
        "top_priorities": ["Retry the analysis", "Review your entered numbers"],
        "budget_recommendations": ["Track expenses manually for now"],
        "savings_strategy": ["Aim to save a fixed % of income each month"],
        "next_month_action_plan": ["Re-run FinWise AI once the service is available"],
    }
