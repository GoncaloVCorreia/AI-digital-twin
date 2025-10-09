"""
Persona domain service.
"""

from __future__ import annotations

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.persona_model import Persona as PersonaModel
from app.schemas.persona import PersonaCreate, PersonaUpdate


class PersonaService:
    """Business logic for personas."""

    @staticmethod
    def create_persona(db: Session, data: PersonaCreate, creator_id: int) -> PersonaModel:
        persona = PersonaModel(**data.model_dump())
        db.add(persona)
        try:
            db.commit()
            db.refresh(persona)
            return persona
        except IntegrityError as e:
            db.rollback()
            # If you later add a UNIQUE constraint (e.g., name), return a 409 at router
            raise e
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_persona(db: Session, persona_id: int) -> Optional[PersonaModel]:
        return db.query(PersonaModel).filter(PersonaModel.id == persona_id).first()

    @staticmethod
    def list_personas(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
    ) -> Tuple[List[PersonaModel], int]:
        q = db.query(PersonaModel)
        if search:
            s = f"%{search}%"
            q = q.filter(
                or_(
                    PersonaModel.name.ilike(s),
                    PersonaModel.location.ilike(s),
                    PersonaModel.description.ilike(s),
                )
            )
        total = q.count()
        rows = q.order_by(PersonaModel.id.asc()).offset(skip).limit(limit).all()
        return rows, total

    @staticmethod
    def update_persona(
        db: Session, persona_id: int, patch: PersonaUpdate
    ) -> Optional[PersonaModel]:
        persona = db.query(PersonaModel).filter(PersonaModel.id == persona_id).first()
        if not persona:
            return None

        for k, v in patch.model_dump(exclude_unset=True).items():
            setattr(persona, k, v)

        try:
            db.commit()
            db.refresh(persona)
            return persona
        except IntegrityError as e:
            db.rollback()
            raise e
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def delete_persona(db: Session, persona_id: int) -> bool:
        persona = db.query(PersonaModel).filter(PersonaModel.id == persona_id).first()
        if not persona:
            return False
        try:
            db.delete(persona)
            db.commit()
            return True
        except SQLAlchemyError:
            db.rollback()
            raise
