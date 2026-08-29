"""
app.py
------
FinWise AI - Streamlit entry point.
Run with:  streamlit run app.py
"""

import streamlit as st

from src import config
from src.financial_calculator import (
    calculate_totals,
    calculate_preliminary_score,
    build_expense_breakdown,
)
from src.cache_manager import configure_cache
from src.chains import build_llm, run_financial_analysis, stream_recommendations, demo_raw_messages

st.set_page_config(page_title=config.APP_TITLE, page_icon="💰", layout="wide")

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "calc_result" not in st.session_state:
    st.session_state.calc_result = None
if "preliminary_score" not in st.session_state:
    st.session_state.preliminary_score = None
if "cache_status" not in st.session_state:
    st.session_state.cache_status = configure_cache("memory")

# ============================================================================
# GATE — the app is locked until the visitor enters their own OpenAI API key.
# Nothing below this block runs until a key is present in session_state.
# ============================================================================
if "user_api_key" not in st.session_state:
    # Falls back to a local .env key only if one exists (useful for your own
    # local testing) — on the deployed app this will normally be empty, so
    # every visitor is asked for their own key.
    st.session_state.user_api_key = config.OPENAI_API_KEY

if not st.session_state.user_api_key:
    st.title(f"💰 {config.APP_TITLE}")
    st.caption(config.APP_TAGLINE)
    st.info(config.EDUCATIONAL_DISCLAIMER)

    st.subheader("🔑 Enter your OpenAI API key to continue")
    st.write(
        "FinWise AI needs your own OpenAI API key to run. It's used only "
        "for this session — never stored, logged, or saved anywhere."
    )
    with st.form("api_key_gate"):
        key_input = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        unlock = st.form_submit_button("Unlock FinWise AI", type="primary")
    if unlock:
        if key_input.strip():
            st.session_state.user_api_key = key_input.strip()
            st.rerun()
        else:
            st.warning("Please paste a valid API key.")
    st.caption(
        "Don't have one? Create a free OpenAI account and generate a key at "
        "platform.openai.com/api-keys."
    )
    st.stop()

active_api_key = st.session_state.user_api_key

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title(f"💰 {config.APP_TITLE}")
    st.caption(config.APP_TAGLINE)
    st.info(config.EDUCATIONAL_DISCLAIMER)

    st.divider()
    st.success("🔑 API key active for this session.")
    if st.button("Change / clear API key"):
        st.session_state.user_api_key = ""
        st.rerun()

    st.divider()
    st.subheader("⚙️ Model Settings")
    model_name = st.text_input("OpenAI model", value=config.DEFAULT_MODEL)
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, config.DEFAULT_TEMPERATURE, 0.1)

    st.subheader("🗄️ Caching")
    cache_choice_label = st.selectbox("Cache backend", list(config.CACHE_OPTIONS.keys()))
    cache_choice = config.CACHE_OPTIONS[cache_choice_label]
    if st.button("Apply cache setting"):
        st.session_state.cache_status = configure_cache(cache_choice)
    st.caption(st.session_state.cache_status)

    st.divider()
    if st.button("🔄 Reset session"):
        for key in ["analysis_result", "calc_result", "preliminary_score"]:
            st.session_state[key] = None
        st.rerun()

    st.divider()
    st.caption("Built with LangChain + Streamlit • Educational prototype only.")

# ---------------------------------------------------------------------------
# Main page - input form
# ---------------------------------------------------------------------------
st.header("📋 Your Monthly Financial Snapshot")
st.caption(config.EDUCATIONAL_DISCLAIMER)

with st.form("financial_form"):
    col1, col2 = st.columns(2)
    with col1:
        monthly_income = st.number_input("Monthly income", min_value=0.0, step=100.0, value=5000.0)
        current_savings = st.number_input("Current monthly savings", min_value=0.0, step=50.0, value=500.0)
    with col2:
        financial_goal = st.selectbox("Financial goal", config.FINANCIAL_GOALS)
        currency = st.selectbox("Currency", config.CURRENCIES)

    st.markdown("#### Monthly Expenses")
    expense_tabs = st.tabs(list(config.EXPENSE_CATEGORIES.values()))
    expenses = {}
    default_values = {
        "housing": 1200.0, "food": 400.0, "transportation": 200.0, "utilities": 150.0,
        "education": 0.0, "healthcare": 100.0, "entertainment": 150.0,
        "loan_debt": 300.0, "other": 100.0,
    }
    for tab, (key, label) in zip(expense_tabs, config.EXPENSE_CATEGORIES.items()):
        with tab:
            expenses[key] = st.number_input(
                f"{label} ({currency})", min_value=0.0, step=10.0,
                value=default_values.get(key, 0.0), key=f"exp_{key}"
            )

    with st.expander("ℹ️ How is this used?"):
        st.write(
            "Python calculates your totals and ratios first. Those numbers are then "
            "sent to the LLM, which generates educational insights only - it never "
            "sees or stores any real bank details."
        )

    submitted = st.form_submit_button("🔍 Analyze My Budget", use_container_width=True)

# ---------------------------------------------------------------------------
# Run calculations + AI analysis on submit
# ---------------------------------------------------------------------------
if submitted:
    calc = calculate_totals(monthly_income, expenses, current_savings)
    score = calculate_preliminary_score(monthly_income, expenses, current_savings)
    st.session_state.calc_result = calc
    st.session_state.preliminary_score = score

    llm_inputs = {
        "monthly_income": calc["monthly_income"],
        "total_expenses": calc["total_expenses"],
        "remaining_income": calc["remaining_income"],
        "savings": calc["savings"],
        "savings_ratio": calc["savings_ratio"],
        "expense_ratio": calc["expense_ratio"],
        "financial_goal": financial_goal,
        "expense_breakdown": build_expense_breakdown(expenses),
    }

    if active_api_key:
        with st.spinner("FinWise AI is analyzing your budget..."):
            llm = build_llm(model_name=model_name, temperature=temperature, api_key=active_api_key)
            result = run_financial_analysis(llm, llm_inputs, score)
            st.session_state.analysis_result = result
            st.session_state.llm_inputs = llm_inputs
    else:
        st.error("Cannot run AI analysis without an OpenAI API key. See the sidebar warning above.")

# ---------------------------------------------------------------------------
# Financial overview (always shown once calculated)
# ---------------------------------------------------------------------------
if st.session_state.calc_result:
    calc = st.session_state.calc_result
    st.divider()
    st.header("📊 Financial Overview")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Monthly Income", f"{calc['monthly_income']:,.2f}")
    m2.metric("Total Expenses", f"{calc['total_expenses']:,.2f}")
    m3.metric("Remaining Balance", f"{calc['remaining_income']:,.2f}")
    m4.metric("Current Savings", f"{calc['savings']:,.2f}")

    r1, r2 = st.columns(2)
    r1.metric("Savings Ratio", f"{calc['savings_ratio']:.1f}%")
    r2.metric("Expense Ratio", f"{calc['expense_ratio']:.1f}%")

# ---------------------------------------------------------------------------
# AI Analysis dashboard
# ---------------------------------------------------------------------------
if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    score = st.session_state.preliminary_score

    st.divider()
    st.header("🤖 AI Financial Analysis")
    st.caption(config.EDUCATIONAL_DISCLAIMER)

    tab_overview, tab_spending, tab_plan, tab_raw = st.tabs(
        ["Overview", "Spending Analysis", "Action Plan", "Rule-based vs AI"]
    )

    with tab_overview:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Financial Health Score (AI)")
            ai_score = result["financial_health_score"]
            st.progress(ai_score / 100)
            label, status = config.get_score_band(ai_score)
            getattr(st, status)(f"Score: {ai_score}/100 — {label}")
        with col_b:
            st.subheader("Risk Level")
            risk = result.get("risk_level", "MEDIUM")
            risk_icon = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}.get(risk, "🟡")
            st.markdown(f"### {risk_icon} {risk}")

        st.subheader("Summary")
        st.write(result.get("financial_summary", ""))

        st.subheader("Top Priorities")
        for p in result.get("top_priorities", []):
            st.markdown(f"- {p}")

        st.subheader("💬 Live Streamed Recommendation")
        if st.button("Generate streaming recommendation"):
            llm = build_llm(model_name=model_name, temperature=temperature, streaming=True, api_key=active_api_key)
            st.write_stream(stream_recommendations(llm, st.session_state.llm_inputs))

    with tab_spending:
        st.subheader("Spending Analysis by Category")
        for item in result.get("spending_analysis", []):
            with st.expander(f"📁 {item.get('category', 'Category')}"):
                st.write(f"**Observation:** {item.get('observation', '')}")
                st.write(f"**Recommendation:** {item.get('recommendation', '')}")

    with tab_plan:
        col_c, col_d = st.columns(2)
        with col_c:
            st.subheader("💡 Budget Recommendations")
            for rec in result.get("budget_recommendations", []):
                st.markdown(f"- {rec}")
            st.subheader("🏦 Savings Strategy")
            for s in result.get("savings_strategy", []):
                st.markdown(f"- {s}")
        with col_d:
            st.subheader("📅 Next Month Action Plan")
            for step in result.get("next_month_action_plan", []):
                st.markdown(f"- {step}")

    with tab_raw:
        st.subheader("Rule-based Preliminary Score vs AI Score")
        c1, c2 = st.columns(2)
        c1.metric("Python Rule-based Score", f"{score}/100")
        c2.metric("AI-generated Score", f"{result['financial_health_score']}/100")
        st.caption(
            "The rule-based score is a deterministic heuristic computed purely in "
            "Python (financial_calculator.py). The AI score comes from the LLM's "
            "structured JSON response and may reason more holistically about your "
            "situation - both are educational estimates, not financial advice."
        )

        if st.checkbox("Show raw System/Human/AI message demo"):
            llm = build_llm(model_name=model_name, temperature=temperature, api_key=active_api_key)
            demo = demo_raw_messages(llm, str(st.session_state.calc_result))
            st.json(demo)

st.divider()
st.caption(config.EDUCATIONAL_DISCLAIMER)
