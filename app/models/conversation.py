from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text
# app/models/conversation.py
from sqlalchemy.dialects.postgresql import JSONB


from app.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    interviewer_id = Column(Integer, ForeignKey("interviewers.id", ondelete="CASCADE"))
    persona = Column(String, nullable=False)
    session_id = Column(String, unique=False, nullable=False)
    messages = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
