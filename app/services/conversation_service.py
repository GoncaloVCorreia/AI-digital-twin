from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationDBCreate
from sqlalchemy import asc, desc
from typing import List


class ConversationService:
    @staticmethod
    def create_conversation(db: Session, data: ConversationDBCreate):
        conversation = Conversation(**data.model_dump())
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def get_user_conversations(db: Session, interviewer_id: int):
        return db.query(Conversation).filter(Conversation.interviewer_id == interviewer_id).all()
    
    @staticmethod
    def get_all(db: Session) -> List[Conversation]:
        # newest first
        return (
            db.query(Conversation)
            .order_by(desc(Conversation.created_at), desc(Conversation.id))
            .all()
        )

    @staticmethod
    def get_by_session(db: Session, session_id: str) -> Conversation:
        # show whole thread history for that session (conversation), oldest -> newest
         return (
            db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .order_by(desc(Conversation.created_at), desc(Conversation.id))
            .first()
        )

    @staticmethod
    def get_by_interviewer(db: Session, interviewer_id: int) -> List[Conversation]:
        """
        Return the latest conversation row per session for this interviewer,
        ordered newest -> oldest across sessions.
        """
        return (
            db.query(Conversation)
            .filter(Conversation.interviewer_id == interviewer_id)
            # order so DISTINCT ON picks the newest row per session_id
            .order_by(
                Conversation.session_id,                 # group key for DISTINCT ON
                desc(Conversation.created_at),           # newest first within session
                desc(Conversation.id),                   # tiebreaker
            )
            .distinct(Conversation.session_id)          # PostgreSQL DISTINCT ON (session_id)
            # final presentation order across sessions
            .order_by(desc(Conversation.created_at), desc(Conversation.id))
            .all()
        )
