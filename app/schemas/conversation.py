# app/schemas/chat.py (or conversation.py if you prefer keeping name)
from datetime import datetime
from typing import List, Literal, Optional, Union, Dict, Any
from pydantic import BaseModel
from uuid import uuid4



# ---- Request payload coming from the client ----
class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    persona: Union[int, str] 
    session_id: Optional[str] = None  # optional; server can generate if not provided
    messages: List[ChatMessage]  # parsed by FastAPI (no json.loads)

# ---- What we persist (choose ONE of the two options) ----
# OPTION A: DB column is JSON/JSONB -> keep Python structures
#     (SQLAlchemy Column(JSON) on PostgreSQL; consider MutableDict/MutableList for in-place updates)
class ConversationDBCreate(BaseModel):
    interviewer_id: int
    persona: str
    session_id: str
    messages: Union[List[Dict[str, Any]], Dict[str, Any]]

# OPTION B: DB column is TEXT -> store dumps
# class ConversationDBCreate(BaseModel):
#     interviewer_id: int
#     persona: str
#     session_id: str
#     messages: str  # json.dumps(...) before saving

# ---- What we return to the client ----
class ConversationResponse(BaseModel):
    id: int
    interviewer_id: int
    persona: str
    session_id: str
    # If you want to return parsed messages, use the JSON-friendly type:
    messages: Union[List[Dict[str, Any]], Dict[str, Any]]
    created_at: datetime

    model_config = {"from_attributes": True}  # pydantic v2
