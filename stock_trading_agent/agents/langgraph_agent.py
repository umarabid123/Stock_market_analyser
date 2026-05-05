"""Optional LangGraph agent wrapper.

The module is safe to import even when `langgraph` is not installed.
"""

from __future__ import annotations


def is_langgraph_available() -> bool:
    try:
        import langgraph  # noqa: F401

        return True
    except ImportError:
        return False


def build_agent() -> str:
    """Return a descriptive status instead of failing when optional deps are missing."""
    if not is_langgraph_available():
        return "LangGraph not installed. Install it to enable advanced agent workflows."
    return "LangGraph is available and ready to integrate."
