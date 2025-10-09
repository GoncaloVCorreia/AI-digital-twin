from __future__ import annotations
import anyio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from .manager import ConnectionManager
from .schemas import WSMessage
from pathlib import Path
from src.personas.persona import load_persona 

router = APIRouter()
manager = ConnectionManager()

BASE_DIR = Path(__file__).resolve().parents[2]         
PERSONAS_DIR = BASE_DIR / "src" / "personas_json" 

@router.websocket("/ws/chat")
async def ws_chat(
    websocket: WebSocket,
    room: str = Query(...),
    user: str = Query(...),
    persona: str = Query("default"),
):
    await manager.connect(room, websocket)

    try:
        per = load_persona(persona, persona_dir=str(PERSONAS_DIR))
        system_prompt = per.build_prompt()
    except Exception as e:
        await manager.send_personal(websocket, {"type": "error", "text": f"Persona: {e}"})
        return

    await manager.broadcast(room, {"type": "system", "event": "join", "user": user})

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = WSMessage.model_validate_json(raw)
            except Exception:
                await manager.send_personal(websocket, {"type": "error", "text": "JSON inválido"})
                continue

            if msg.type == "chat" and msg.text:
                await manager.broadcast(room, {"type": "chat", "user": msg.user or user, "text": msg.text})

                runner = websocket.app.state.graph_runner  
                def _call():
                    return runner.stream_response(msg.text, system_prompt)
                reply = await anyio.to_thread.run_sync(_call)

                await manager.broadcast(room, {"type": "chat", "user": f"{persona}-bot", "text": reply})
            else:
                await manager.send_personal(websocket, {"type": "error", "text": "Tipo de mensagem não suportado"})

    except WebSocketDisconnect:
        manager.disconnect(room, websocket)
        await manager.broadcast(room, {"type": "system", "event": "leave", "user": user})
