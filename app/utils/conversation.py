from typing import Any, Dict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage  # for typing/role mapping
from uuid import uuid4

def _msg_to_dict(m: Any) -> Dict[str, str]:
    """Normalize LangChain/LangGraph message objects into {role, content}."""
    # If it's already a dict-like from somewhere else:
    if isinstance(m, dict) and "content" in m:
        role = m.get("role") or m.get("type") or "user"
        # map common LangChain types to OpenAI-ish roles
        if role == "human": role = "user"
        if role == "ai":    role = "assistant"
        return {"role": role, "content": m.get("content", "")}

    # LangChain BaseMessage subclasses:
    if isinstance(m, BaseMessage):
        if isinstance(m, HumanMessage):
            role = "user"
        elif isinstance(m, AIMessage):
            role = "assistant"
        elif isinstance(m, SystemMessage):
            role = "system"
        else:
            # fall back to .type if custom tool/function messages appear
            role = getattr(m, "type", "user")
            if role == "human": role = "user"
            if role == "ai":    role = "assistant"
        content = getattr(m, "content", "")
        return {"role": role, "content": content}

    # Fallback: stringify anything unexpected
    return {"role": "user", "content": str(m)}

def _new_session_id() -> str:
    return f"session-{uuid4().hex[:12]}"