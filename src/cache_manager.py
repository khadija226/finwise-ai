"""
cache_manager.py
-----------------
Registers a global LangChain LLM cache so repeated identical prompts do not
trigger a new API call (saves cost + is faster).

set_llm_cache(...) registers ONE global cache. LangChain checks this cache
before making a call to the model, keyed on (prompt text + model params).

Two backends are supported:
  - InMemoryCache -> lives in RAM, fastest, cleared when the app restarts.
  - SQLiteCache    -> lives in a .db file on disk, survives restarts.
"""

from langchain_core.globals import set_llm_cache
from langchain_community.cache import InMemoryCache, SQLiteCache

from src.config import SQLITE_CACHE_PATH


def configure_cache(cache_type: str = "memory") -> str:
    """
    Configure the global LangChain LLM cache.

    cache_type: "memory" | "sqlite" | "none"
    Returns a short human-readable status string.
    """
    if cache_type == "memory":
        set_llm_cache(InMemoryCache())
        return "In-memory cache active (cleared on restart)."

    if cache_type == "sqlite":
        set_llm_cache(SQLiteCache(database_path=SQLITE_CACHE_PATH))
        return f"SQLite cache active at ./{SQLITE_CACHE_PATH} (persists across restarts)."

    # "none" -> disable caching entirely
    set_llm_cache(None)
    return "Caching disabled - every request calls the model."
