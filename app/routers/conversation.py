from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.conversation import ChatRequest, ConversationDBCreate, ConversationResponse
from app.services.conversation_service import ConversationService
from app.schemas.interviewers import User
from app.utils.dependencies import get_current_user

from src.chatbot.chat_graph import ChatGraphRunner
from src.configs.groq_config import ConfigGroq
from src.llm.llm import GroqLLM
from src.personas.persona import load_persona
from typing import Any, Dict, List
from app.utils.conversation import _msg_to_dict, _new_session_id
from app.runtime import get_runner

import logging
rlog = logging.getLogger("chat.router")

router = APIRouter(prefix="/chat", tags=["chat"])



# 1) Get ALL conversations (returns: id, interviewer_id, persona, session_id, messages, created_at)
@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # If you want to restrict this to admins, uncomment below:
    # if not current_user.is_superuser:
    #     raise HTTPException(status_code=403, detail="Admins only")
    return ConversationService.get_all(db)

# 2) Get by session_id
@router.get("/conversations/by-session/{session_id}", response_model=ConversationResponse)
async def conversations_by_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Path params are validated by FastAPI and passed in here. :contentReference[oaicite:1]{index=1}
    row = ConversationService.get_by_session(db, session_id)
    if not row:
        raise HTTPException(status_code=404, detail="No conversations for this session_id")
    return row

# 3) Get by interviewer_id
@router.get("/conversations/by-interviewer/{interviewer_id}", response_model=List[ConversationResponse])
async def conversations_by_interviewer(
    interviewer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = ConversationService.get_by_interviewer(db, interviewer_id)
    if not rows:
        raise HTTPException(status_code=404, detail="No conversations for this interviewer")
    return rows

@router.post("/respond", response_model=ConversationResponse)
async def chat_respond(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rlog.info("chat_respond: ENTER")
    runner = get_runner()
    rlog.info("chat_respond: got runner")
    # NEW: ensure we have a session_id
    session_id = data.session_id or _new_session_id()
    rlog.info("chat_respond: session_id=%s", session_id)


    # 1) Persona → system prompt
    try:
        persona = load_persona(data.persona, persona_dir="src/personas_json")
        system_prompt = persona.build_prompt()
        rlog.info("chat_respond: persona loaded: %s", data.persona)
    except Exception as e:
        rlog.exception("chat_respond: persona error")
        raise HTTPException(status_code=400, detail=f"Invalid persona: {str(e)}")

    # 2) Last user message from request (you’re still sending a list in ChatRequest)
    try:
        user_msg = next(m.content for m in reversed(data.messages) if m.role == "user")
        rlog.info("chat_respond: got user_msg (%d chars)", len(user_msg))
    except StopIteration:
        raise HTTPException(status_code=400, detail="Missing user message")

    # 3) Invoke graph (this will persist the new checkpoint in Postgres)
    rlog.info("chat_respond: invoking stream_response()")
    ai_response = runner.stream_response(
        user_input=user_msg,
        system_message=system_prompt,
        session_id=session_id,
    )
    rlog.info("chat_respond: got ai_response (%s)", "yes" if ai_response else "no")
    # 4) Pull full thread state from LangGraph and normalize to [{role, content}, ...]
    snapshot = runner.graph.get_state({"configurable": {"thread_id": session_id}})
    state_msgs = snapshot.values.get("messages", []) if snapshot and snapshot.values else []
    rlog.info("chat_respond: state_msgs count=%d", len(state_msgs))
    # If, for any reason, state was empty, fall back to current turn only
    if not state_msgs:
        state_msgs = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": ai_response},
        ]

    full_history: List[Dict[str, str]] = [_msg_to_dict(m) for m in state_msgs]

    # 5) Persist JSONB directly (no dumps needed)
    saved = ConversationService.create_conversation(
        db,
        ConversationDBCreate(
            interviewer_id=current_user.id,
            persona=data.persona,
            session_id=session_id,
            messages=full_history,  # JSONB column
        ),
    )
    rlog.info("chat_respond: saved conversation id=%s", saved.id)
    return saved
