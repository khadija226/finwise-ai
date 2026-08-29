"""
prompts.py
----------
All prompt engineering lives here:
  - the system / safety instructions
  - the JSON schema the LLM must return
  - a reusable PromptTemplate (single string)
  - a reusable ChatPromptTemplate (system + human messages) for JSON output
  - a second ChatPromptTemplate used purely for the streamed narrative text
"""

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

# ---------------------------------------------------------------------------
# System / safety instructions
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are FinWise AI, an educational personal-finance assistant.

Your job is to help a user understand their monthly budget using the numbers
they and a Python program have already calculated. You explain patterns,
suggest budgeting ideas, and highlight risks in clear, friendly language.

SAFETY RULES (must always be followed):
1. You are for EDUCATIONAL PURPOSES ONLY. Never claim to give guaranteed,
   personalized investment or legal advice.
2. Never promise a specific financial outcome (e.g. "you will be debt-free
   in 6 months"). Use words like "may", "could", "consider".
3. Always gently encourage the user to consult a qualified financial
   professional for real decisions.
4. Never ask for or reference real bank account numbers, passwords, or
   other sensitive identifying information.
5. Base your analysis ONLY on the numbers provided - do not invent data.
6. Keep tone supportive and non-judgmental, even when the numbers are bad.
"""

# ---------------------------------------------------------------------------
# JSON schema description (kept as a plain string so it can be dropped
# straight into any prompt)
# ---------------------------------------------------------------------------
JSON_SCHEMA_DESCRIPTION = """
Return ONLY valid JSON (no markdown fences, no commentary before or after)
matching EXACTLY this schema:

{
  "financial_summary": "string - a short 2-3 sentence overview",
  "financial_health_score": 0,
  "spending_analysis": [
    { "category": "string", "observation": "string", "recommendation": "string" }
  ],
  "risk_level": "LOW | MEDIUM | HIGH",
  "top_priorities": ["string", "string"],
  "budget_recommendations": ["string", "string"],
  "savings_strategy": ["string", "string"],
  "next_month_action_plan": ["string", "string"]
}

Rules:
- "financial_health_score" must be an integer between 0 and 100.
- "risk_level" must be exactly one of: LOW, MEDIUM, HIGH.
- Every array must contain at least 2 items.
- Do not wrap the JSON in ```json code fences. Return raw JSON only.
"""

# ---------------------------------------------------------------------------
# PromptTemplate - reusable single-string template
# ---------------------------------------------------------------------------
FINANCIAL_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=[
        "monthly_income",
        "total_expenses",
        "remaining_income",
        "savings",
        "savings_ratio",
        "expense_ratio",
        "financial_goal",
        "expense_breakdown",
    ],
    template="""
Analyse the following monthly financial snapshot:

- Monthly income: {monthly_income}
- Total expenses: {total_expenses}
- Remaining income after expenses: {remaining_income}
- Current savings this month: {savings}
- Savings ratio: {savings_ratio}%
- Expense ratio: {expense_ratio}%
- Financial goal: {financial_goal}

Expense breakdown by category:
{expense_breakdown}

"""
    + JSON_SCHEMA_DESCRIPTION,
)

# ---------------------------------------------------------------------------
# ChatPromptTemplate - system + human messages, used for structured JSON
# ---------------------------------------------------------------------------
FINANCIAL_CHAT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            "Here is my financial snapshot for this month:\n\n"
            "- Monthly income: {monthly_income}\n"
            "- Total expenses: {total_expenses}\n"
            "- Remaining income after expenses: {remaining_income}\n"
            "- Current savings this month: {savings}\n"
            "- Savings ratio: {savings_ratio}%\n"
            "- Expense ratio: {expense_ratio}%\n"
            "- Financial goal: {financial_goal}\n\n"
            "Expense breakdown by category:\n{expense_breakdown}\n\n"
            + JSON_SCHEMA_DESCRIPTION,
        ),
    ]
)

# ---------------------------------------------------------------------------
# A second ChatPromptTemplate used ONLY for the streamed, human-readable
# narrative recommendation shown live in the UI (not JSON).
# ---------------------------------------------------------------------------
NARRATIVE_CHAT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            "Based on this financial snapshot, write a short, warm, "
            "encouraging paragraph (4-6 sentences) with practical budgeting "
            "suggestions. Do NOT use JSON here - plain conversational text only.\n\n"
            "- Monthly income: {monthly_income}\n"
            "- Total expenses: {total_expenses}\n"
            "- Remaining income after expenses: {remaining_income}\n"
            "- Savings ratio: {savings_ratio}%\n"
            "- Expense ratio: {expense_ratio}%\n"
            "- Financial goal: {financial_goal}\n\n"
            "Expense breakdown:\n{expense_breakdown}",
        ),
    ]
)
