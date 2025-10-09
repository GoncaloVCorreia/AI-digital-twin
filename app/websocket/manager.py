from __future__ import annotations
from typing import Dict, Set
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    """
    Gere clientes por 'room'. Permite broadcast e mensagens individuais.
    """
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room: str, websocket: WebSocket):
        await websocket.accept()
        self.rooms.setdefault(room, set()).add(websocket)

    def disconnect(self, room: str, websocket: WebSocket):
        if room in self.rooms and websocket in self.rooms[room]:
            self.rooms[room].remove(websocket)
            if not self.rooms[room]:
                del self.rooms[room]

    async def send_personal(self, websocket: WebSocket, message: dict):
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, room: str, message: dict):
        if room not in self.rooms:
            return
        data = json.dumps(message)
        to_remove = []
        for ws in list(self.rooms[room]):
            try:
                await ws.send_text(data)
            except Exception:
                to_remove.append(ws)
        for ws in to_remove:
            self.disconnect(room, ws)

    async def heartbeat(self, websocket: WebSocket, interval=30):
        """Opcional: envio de pings periódicos."""
        try:
            while True:
                await asyncio.sleep(interval)
                await websocket.send_text(json.dumps({
                    "type": "system",
                    "event": "ping",
                    "ts": datetime.utcnow().isoformat()
                }))
        except Exception:
            return
