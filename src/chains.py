"""
chains.py
---------
Everything that actually talks to the LLM:
  - build_llm(): creates a ChatOpenAI instance
  - build_financial_chain(): a reusable LLMChain that returns raw JSON text
  - demo_raw_messages(): shows SystemMessage / HumanMessage / AIMessage directly
  - stream_recommendations(): streams a narrative recommendation for the UI
  - run_financial_analysis(): high-level helper used by app.py
"""

from typing import Dict, Generator

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_classic.chains import LLMChain

from src.config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, OPENAI_API_KEY
from src.prompts import (
    SYSTEM_PROMPT,
    FINANCIAL_PROMPT_TEMPLATE,
    NARRATIVE_CHAT_TEMPLATE,
)
from src.utils import safe_parse_json, fallback_response


def build_llm(model_name: str = DEFAULT_MODEL, temperature: float = DEFAULT_TEMPERATURE,
              streaming: bool = False, api_key: str = None) -> ChatOpenAI:
    """Create a configured ChatOpenAI instance.

    `api_key` lets the caller pass a key entered by the user in the UI
    (e.g. on Streamlit Cloud, where each visitor supplies their own key).
    Falls back to OPENAI_API_KEY from config (env var / .env / st.secrets)
    when no key is passed in, which is convenient for local development.
    """
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key or OPENAI_API_KEY,
        streaming=streaming,
    )


def build_financial_chain(llm: ChatOpenAI) -> LLMChain:
    """
    Build the reusable LLMChain that turns the financial PromptTemplate
    into a raw JSON string response.
    """
    return LLMChain(llm=llm, prompt=FINANCIAL_PROMPT_TEMPLATE)


def demo_raw_messages(llm: ChatOpenAI, user_summary: str) -> Dict[str, str]:
    """
    Small demo showing how SystemMessage / HumanMessage / AIMessage
    represent a conversation manually (without a prompt template).
    Returns a dict of the three message contents for display in the UI.
    """
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"In one sentence, how does my budget look? {user_summary}"),
    ]
    ai_reply = llm.invoke(messages)
    # ai_reply is an AIMessage - wrap explicitly to show the type in the demo
    ai_message = AIMessage(content=ai_reply.content)

    return {
        "system": SYSTEM_PROMPT[:200] + "...",
        "human": messages[1].content,
        "ai": ai_message.content,
    }


def run_financial_analysis(llm: ChatOpenAI, inputs: Dict, preliminary_score: int) -> Dict:
    """
    Run the LLMChain to get structured JSON insights.
    Falls back to a safe default if the JSON cannot be parsed.
    """
    chain = build_financial_chain(llm)
    raw_output = chain.run(**inputs)

    parsed = safe_parse_json(raw_output)
    if parsed is None:
        return fallback_response(preliminary_score)
    return parsed


def stream_recommendations(llm: ChatOpenAI, inputs: Dict) -> Generator[str, None, None]:
    """
    Stream a narrative (non-JSON) recommendation for a natural typing effect
    in the Streamlit UI via st.write_stream().
    """
    messages = NARRATIVE_CHAT_TEMPLATE.format_messages(**inputs)
    for chunk in llm.stream(messages):
        if chunk.content:
            yield chunk.content
