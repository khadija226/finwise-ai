"""
financial_calculator.py
------------------------
Deterministic financial maths - NO AI here at all.
Same inputs will always produce the same outputs.
"""

from typing import Dict


def calculate_totals(monthly_income: float, expenses: Dict[str, float], savings: float) -> Dict:
    """
    Compute total expenses, remaining income, savings ratio and expense ratio.

    Guards against divide-by-zero when monthly_income is 0.
    """
    total_expenses = float(sum(expenses.values()))
    remaining_income = float(monthly_income) - total_expenses

    if monthly_income and monthly_income > 0:
        savings_ratio = (savings / monthly_income) * 100
        expense_ratio = (total_expenses / monthly_income) * 100
    else:
        # Avoid division by zero - treat as undefined / worst case
        savings_ratio = 0.0
        expense_ratio = 0.0 if total_expenses == 0 else 999.0

    return {
        "monthly_income": round(float(monthly_income), 2),
        "total_expenses": round(total_expenses, 2),
        "remaining_income": round(remaining_income, 2),
        "savings": round(float(savings), 2),
        "savings_ratio": round(savings_ratio, 2),
        "expense_ratio": round(expense_ratio, 2),
    }


def calculate_preliminary_score(monthly_income: float, expenses: Dict[str, float], savings: float) -> int:
    """
    Weighted 0-100 heuristic based on:
      - savings ratio      (30%)
      - leftover / remaining income ratio (30%)
      - expense ratio       (25%, inverted - lower is better)
      - debt burden (loan_debt share of income) (15%, inverted)

    This is a simple, transparent rule-based score - NOT the AI's opinion.
    It gives the LLM a deterministic starting point to reason from.
    """
    if not monthly_income or monthly_income <= 0:
        return 0

    total_expenses = sum(expenses.values())
    remaining_income = monthly_income - total_expenses

    savings_ratio = max(0.0, min((savings / monthly_income) * 100, 100))
    remaining_ratio = max(0.0, min((remaining_income / monthly_income) * 100, 100))
    expense_ratio = (total_expenses / monthly_income) * 100
    debt_ratio = (expenses.get("loan_debt", 0.0) / monthly_income) * 100

    # --- Component scores (each already 0-100) ---
    savings_score = min(savings_ratio * 2, 100)          # 50% savings ratio -> full marks
    leftover_score = min(remaining_ratio * 2, 100)        # 50% leftover -> full marks

    # Expense ratio: 0-50% is great, 100%+ is terrible
    expense_score = max(0.0, 100 - max(0.0, expense_ratio - 50) * 2)

    # Debt burden: 0% is great, 40%+ of income on debt is terrible
    debt_score = max(0.0, 100 - debt_ratio * 2.5)

    weighted = (
        savings_score * 0.30
        + leftover_score * 0.30
        + expense_score * 0.25
        + debt_score * 0.15
    )

    return int(round(max(0, min(weighted, 100))))


def build_expense_breakdown(expenses: Dict[str, float]) -> str:
    """Human-readable, LLM-friendly summary of expense categories."""
    lines = [f"- {k}: {v:.2f}" for k, v in expenses.items() if v > 0]
    return "\n".join(lines) if lines else "No expenses entered."
