from pydantic import BaseModel, Field
from typing import Optional, Literal

MessageType = Literal["join", "chat", "system", "error"]

class WSMessage(BaseModel):
    type: MessageType = Field(..., description="join | chat | system | error")
    text: Optional[str] = None    
    user: Optional[str] = None    
