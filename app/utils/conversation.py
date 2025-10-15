from typing import Any, Dict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage  # for typing/role mapping
from uuid import uuid4

def _prompt_from_persona_row(p) -> str:
    """
    Build the system prompt from a Persona ORM row.
    Fields available (per your schema):
      name, age, location, description, education, tech_skills,
      soft_skills, strenghts, weaknesses, goals, hobbies, personality
    """
    return (
        f"You are role-playing as the following persona.\n\n"
        f"Name: {p.name}\n"
        f"Age: {p.age}\n"
        f"Location: {p.location}\n"
        f"Personality: {p.personality}\n"
        f"Description: {p.description}\n"
        f"Education: {p.education}\n"
        f"Technical skills: {p.tech_skills}\n"
        f"Soft skills: {p.soft_skills}\n"
        f"Strengths: {p.strenghts}\n"          # note: DB column is 'strenghts'
        f"Weaknesses: {p.weaknesses}\n"
        f"Goals: {p.goals}\n"
        f"Hobbies: {p.hobbies}\n\n"
        f"Stay in character. Be helpful, concise, and consistent with the persona."
    )

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