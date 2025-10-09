"""
Persona API endpoints.
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.schemas.persona import (
    Persona,
    PersonaCreate,
    PersonaUpdate,
    PaginatedResponse,
)
from app.services.persona_service import PersonaService

router = APIRouter(prefix="/personas", tags=["personas"])


@router.post("/", response_model=Persona, status_code=status.HTTP_201_CREATED)
def create_persona(payload: PersonaCreate, db: Session = Depends(get_db)):
    try:
        created = PersonaService.create_persona(db, payload)
        return created
    except IntegrityError:
        # If you later add a UNIQUE constraint (e.g., name) we surface 409 here.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Persona already exists",
        )


@router.get("/", response_model=PaginatedResponse[Persona])
def list_personas(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=128),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    items, total = PersonaService.list_personas(db, skip=skip, limit=limit, search=search)
    return PaginatedResponse[Persona](
        items=items,
        total=total,
        page=page,
        limit=limit,
        has_next=skip + limit < total,
        has_prev=page > 1,
    )


@router.get("/{persona_id}", response_model=Persona)
def get_persona(persona_id: int, db: Session = Depends(get_db)):
    row = PersonaService.get_persona(db, persona_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
    return row


@router.put("/{persona_id}", response_model=Persona)
def update_persona(
    persona_id: int,
    payload: PersonaUpdate,
    db: Session = Depends(get_db),
):
    updated = PersonaService.update_persona(db, persona_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
    return updated


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_persona(persona_id: int, db: Session = Depends(get_db)):
    ok = PersonaService.delete_persona(db, persona_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
