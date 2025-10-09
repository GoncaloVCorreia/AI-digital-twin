"""
Persona Pydantic schemas.
"""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


# ---------- Persona Schemas ----------

MAX_LEN = 512


class PersonaBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=MAX_LEN)
    age: int = Field(..., ge=0, le=120)
    location: str = Field(..., min_length=1, max_length=MAX_LEN)
    description: str = Field(..., min_length=1, max_length=MAX_LEN)
    education: str = Field(..., min_length=1, max_length=MAX_LEN)
    tech_skills: str = Field(..., min_length=1, max_length=MAX_LEN)
    soft_skills: str = Field(..., min_length=1, max_length=MAX_LEN)
    # Kept original column name "strenghts" to match DB
    strenghts: str = Field(..., min_length=1, max_length=MAX_LEN)
    weaknesses: str = Field(..., min_length=1, max_length=MAX_LEN)
    goals: str = Field(..., min_length=1, max_length=MAX_LEN)
    hobbies: str = Field(..., min_length=1, max_length=MAX_LEN)
    personality: str = Field(..., min_length=1, max_length=MAX_LEN)

    @field_validator(
        "name",
        "location",
        "description",
        "education",
        "tech_skills",
        "soft_skills",
        "strenghts",
        "weaknesses",
        "goals",
        "hobbies",
        "personality",
        mode="before",
    )
    @classmethod
    def strip_strings(cls, v: str) -> str:
        if isinstance(v, str):
            vs = v.strip()
            if not vs:
                raise ValueError("Field must be a non-empty string")
            return vs
        return v


class PersonaCreate(PersonaBase):
    """Payload for creating a persona."""
    pass


class PersonaUpdate(BaseModel):
    """Partial update; all fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    age: Optional[int] = Field(None, ge=0, le=120)
    location: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    description: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    education: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    tech_skills: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    soft_skills: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    strenghts: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    weaknesses: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    goals: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    hobbies: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    personality: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)


class Persona(PersonaBase):
    """Response model."""
    id: int

    class Config:
        from_attributes = True
